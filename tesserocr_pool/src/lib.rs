use std::cell::Cell;
use std::sync::{Arc, Barrier, Mutex};
use std::thread::LocalKey;

use numpy::{Ix3, PyReadonlyArray};
use pyo3::{*, prelude::*};
use rayon::{
    prelude::*,
    ThreadPool,
    ThreadPoolBuilder,
};

use tesserocr_pool::tess::TessApi;
use tesserocr_pool::TesserocrError;

#[pyclass]
#[derive(Debug)]
struct TesserocrPool {
    pool: Option<ThreadPool>,
    tessdata_dir: String,
    lang: String,
    psm: u8,
    oem: u8,
}

#[pymethods]
impl TesserocrPool {
    #[args(
    tessdata_dir = r#" "tessdata/" "#,
    lang = r#" "eng" "#,
    psm = "0",
    oem = "1",
    )]
    #[new]
    pub fn new(
        tessdata_dir: impl Into<String>,
        lang: impl Into<String>,
        psm: u8,
        oem: u8,
    ) -> Self {
        let pool = None;
        let tessdata_dir = tessdata_dir.into();
        let lang = lang.into();

        Self { pool, tessdata_dir, lang, psm, oem }
    }

    fn cleanup(&mut self) {
        let _ = self.pool.take();
    }

    pub fn init(&mut self) -> PyResult<()> {
        let tessdata_dir = self.tessdata_dir.clone();
        let lang = self.lang.clone();

        let worker_count = num_cpus::get();
        let init = Arc::new(Mutex::new(vec![]));
        let barrier = Arc::new(Barrier::new(worker_count + 1));

        let init_copy = init.clone();
        let barrier_copy = barrier.clone();

        self.pool = ThreadPoolBuilder::new()
            .num_threads(worker_count)
            .start_handler(move |arg| {
                let init = init_copy.clone();
                let barrier = barrier_copy.clone();
                let tessdata_dir = &tessdata_dir.clone();
                let lang = &lang.clone();

                let result = match TessApi::new(Some(tessdata_dir), lang) {
                    Ok(mut tess_api) => {
                        let ret = tess_api
                            .set_variable("debug_file", "/dev/null")
                            .map(|_| format!("{:?}", &mut tess_api));

                        TESS_API.with(|tls|
                            tls.set(Some(tess_api))
                        );

                        ret
                    }
                    Err(err) => Err(err),
                };

                init
                    .lock()
                    .expect("Initialization result mutex is poisoned")
                    .push((arg, result));

                barrier.wait();
            })
            .build()
            .map_err(|err| TesserocrError::from(err))?
            .into();

        barrier.wait();

        println!("thread count in thread pool is {}", init.lock().unwrap().len());

        init.lock().unwrap().sort_by_key(|&(n, _)| n);
        for (n, r) in init.lock().unwrap().iter() {
            if let Err(err) = r {
                let err = format!("Thread {} failed to start: {}", n, err);
                Err(TesserocrError::from(err))?;
            }
        }

        Ok(())
    }

    fn __enter__(mut self_: PyRefMut<Self>) -> PyResult<PyRefMut<Self>> {
        self_.init()?;
        Ok(self_)
    }

    fn __exit__(mut self_: PyRefMut<Self>, _ty: &PyAny, _vl: &PyAny, _tb: &PyAny) -> PyResult<bool> {
        self_.cleanup();
        Ok(false)
    }

    fn test(&mut self, arr: Vec<Option<PyReadonlyArray<u8, Ix3>>>) {
        for arr in arr {
            if let Some(arr) = arr {
                println!("{:?}", Some(arr.as_ptr()))
            } else {
                let x = None;
                let _ = Some(()) != x;
                println!("{:?}", x)
            }
        }
        println!();
    }

    fn ocr(&mut self, py: Python<'_>, images: Vec<Option<PyReadonlyArray<u8, Ix3>>>, config: Option<&str>) -> PyResult<Vec<Option<String>>> {
        let blacklist = extract_blacklist(config)?;

        let images: Vec<_> = images
            .into_iter()
            .map(|option| match option {
                Some(image) => Some({
                    let shape = image.shape();
                    let (height, width) = if let &[a, b, 3] = shape {
                        (a as u32, b as u32)
                    } else {
                        let err = format!("invalid for rgb image, expected [_, _, 3] but got {:?}", shape);
                        return Err(TesserocrError::from(err));
                    };

                    image.to_vec()
                        .map(|image| (image, width, height))
                        .map_err(|_| r#"invalid layout, please make sure that the array data is in contiguous "C order""#.into())
                }),
                None => None,
            }.transpose())
            .collect::<Result<_, TesserocrError>>()?;

        py.allow_threads(move || if let Some(pool) = &mut self.pool {
            Ok(ocr(pool, images, blacklist)?)
        } else {
            Err(TesserocrError::from("Thread Pool is not initialized").into())
        })
    }
}

fn extract_blacklist(config: Option<&str>) -> Result<Option<&str>, TesserocrError> {
    match config {
        Some(config) if config.contains("blacklist") => Ok(Some(
            config.split(" ")
                .last()
                .ok_or("invalid value for blacklist")?
                .split("=")
                .last()
                .ok_or("invalid value for blacklist")?
        )),
        _ => Ok(None),
    }
}

pub fn ocr(pool: &mut ThreadPool,
           images: Vec<Option<(Vec<u8>, u32, u32)>>,
           blacklist: Option<&str>) -> Result<Vec<Option<String>>, TesserocrError> {
    fn ocr(image: &[u8], width: u32, height: u32,
           blacklist: Option<&str>) -> Result<String, TesserocrError> {
        TESS_API.with(|cell| {
            let mut tess_api = cell.take().unwrap();

            let ret = match blacklist {
                Some(blacklist) =>
                    tess_api.set_variable("tesseract_char_blacklist", blacklist)
                        .and_then(|_| tess_api.ocr(image, width, height)),
                None => tess_api.ocr(image, width, height),
            };

            cell.set(Some(tess_api));

            ret
        })
    }

    const CAP: usize = 5 * 1024 * 1024;
    use async_std::io::BufWriter;
    use std::io::Write;
    use async_std::fs::File;
    use async_std::path::Path;
    use std::hash::{Hash, Hasher};
    use std::borrow::Cow;
    use async_std::io::BufReader;
    use async_std::prelude::*;
    use parallel_stream::*;

    fn hash(item: impl Hash) -> u64 {
        let seed = 0xDEADBEEF;
        let hash = &mut twox_hash::XxHash64::with_seed(seed);
        item.hash(hash);
        hash.finish()
    }

    // store some images on disk (for testing rust code independently from python)
    fn persist_test_images(images: &Vec<Option<(Vec<u8>, u32, u32)>>) {
        let path = &format!("test_images_{:x}.bincode", hash(&images));
        let mut buffer = Vec::with_capacity(CAP);
        bincode::serialize_into(&mut buffer, &images).unwrap();
        std::fs::write(path, &buffer).unwrap();
    }

    persist_test_images(&images);


    match std::fs::create_dir(".cache") {
        Ok(()) => {}
        Err(e) if e.kind() == std::io::ErrorKind::AlreadyExists => {}
        result => result.unwrap()
    }

    type CachedImage<'a> = ((Cow<'a, [u8]>, u32, u32), Cow<'a, str>);

    async fn cache_get(path: impl AsRef<Path>, image_hash: u64, image: &[u8]) -> Option<String> {
        let result: Result<CachedImage, _> = if let Ok(file) = async_std::fs::read(&path).await {
            bincode::deserialize_from(std::io::Cursor::new(file))
        } else {
            return None;
        };

        match result {
            Ok(((cached_image, ..), ocr_result))
            if image_hash == hash(&cached_image) && image == cached_image.as_ref() =>
                return Some(ocr_result.into_owned()),
            _ =>
                None
        }
    }

    async fn cache_put(path: impl AsRef<Path>, image: &[u8], width: u32, height: u32, ocr_result: &str) {
        let image = (Cow::from(image), width, height);
        let value = (image, Cow::from(ocr_result));
        let mut file = Vec::with_capacity(CAP);
        let _ = bincode::serialize_into(&mut file, &value);
        let _ = async_std::fs::write(path, &file).await;
    }

    async fn lookup_or_compute_image(image: &[u8], width: u32, height: u32, blacklist: Option<&str>) -> Result<String, TesserocrError> {
        let image_hash = hash(&image);
        let path = &format!(".cache/{}.bincode", image_hash);
        if let Some(ocr_result) = cache_get(path, image_hash, &image).await {
            return Ok(ocr_result);
        }

        let result = ocr(&image, width, height, blacklist);
        if let Ok(ocr_result) = &result {
            cache_put(path, &image, width, height, ocr_result).await
        }

        result
    }

    let blacklist =  blacklist.map(|x| x.to_owned());
    let vec_result:Vec<_> = async_std::task::block_on(async {
        images
            .into_par_stream()
            // TODO: fork parallel_stream and remove the unnecessary `Copy` bound
            .map(|image| async move {
                let blacklist = blacklist.clone();
                let blacklist = blacklist.as_deref();
                match image {
                    Some((image, width, height)) => Some(lookup_or_compute_image(&image, width, height, blacklist).await),
                    None => None
                }.transpose()
            })
            .collect().await
    });

    vec_result.into_iter().collect()
}

#[pymodule]
fn tesserocr_pool(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<TesserocrPool>()?;

    Ok(())
}

thread_local! {
    static TESS_API: Cell<Option<TessApi>> = Cell::new(None);
}

trait LocalKeyExt<T> {
    fn with<F, R>(&'static self, f: F) -> R
        where
            F: FnOnce(&Cell<Option<T>>) -> R;

    fn with_inner_mut<F, R>(&'static self, f: F) -> R
        where
            F: FnOnce(&mut T) -> R,
    {
        self.with(|cell| {
            let mut tess_api = cell.take().unwrap();
            let ret = f(&mut tess_api);
            cell.set(Some(tess_api));
            ret
        })
    }
}

impl<T> LocalKeyExt<T> for LocalKey<Cell<Option<T>>> {
    fn with<F, R>(&'static self, f: F) -> R where
        F: FnOnce(&Cell<Option<T>>) -> R {
        self.with(f)
    }
}


#[cfg(test)]
mod tests {
    #[test]
    fn show_image() {
        use std::fs::File;
        let file = File::open("../test_images.bincode").unwrap();
        let data: Vec<Option<(Vec<u8>, u32, u32)>> = bincode::deserialize_from(file).unwrap();

        use image::Pixel;
        use minifb::{Window, WindowOptions};

        const WIDTH: usize = 640;
        const HEIGHT: usize = 360;

        let mut window = Window::new(
            "Test - ESC to exit",
            WIDTH,
            HEIGHT,
            WindowOptions::default(),
        )
            .unwrap_or_else(|e| {
                panic!("{}", e);
            });

        // Limit to max ~60 fps update rate
        window.limit_update_rate(Some(std::time::Duration::from_millis(200)));

        // Create a window and display the image.
        for (image, width, height) in data.into_iter().flatten() {
            let image: image::RgbImage = image::ImageBuffer::from_raw(width, height, image).unwrap();

            let image: Vec<_> = image.pixels()
                .map(|pixel| match pixel.channels() {
                    &[r, g, b] => {
                        let (r, g, b) = (r as u32, g as u32, b as u32);
                        (r << 16) | (g << 8) | b
                    }
                    _ => unreachable!(),
                })
                .collect();
            window.update_with_buffer(&image, width as _, height as _).unwrap();
        }
    }
}