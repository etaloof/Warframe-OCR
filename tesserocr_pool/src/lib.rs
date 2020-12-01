use std::cell::Cell;
use std::error::Error;
use std::ffi::NulError;
use std::fmt;
use std::str::Utf8Error;
use std::sync::{Arc, Barrier, Mutex};

use leptess::leptonica::PixError;
use leptess::tesseract::TessInitError;
use numpy::{Ix3, PyReadonlyArray};
use pyo3::{*, prelude::*};
use rayon::{
    prelude::*,
    ThreadPool,
    ThreadPoolBuilder,
    ThreadPoolBuildError,
};

use tess::TessApi;

mod tess;

#[derive(Debug)]
pub struct TesserocrError(String);

impl Error for TesserocrError {}

impl fmt::Display for TesserocrError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}", self.0)
    }
}

impl From<ThreadPoolBuildError> for TesserocrError {
    fn from(value: ThreadPoolBuildError) -> Self {
        Self(value.to_string())
    }
}

impl From<&str> for TesserocrError {
    fn from(value: &str) -> Self {
        Self(value.to_string())
    }
}

impl From<String> for TesserocrError {
    fn from(value: String) -> Self {
        Self(value)
    }
}

impl From<TesserocrError> for PyErr {
    fn from(value: TesserocrError) -> Self {
        value.into()
    }
}

impl From<PixError> for TesserocrError {
    fn from(value: PixError) -> Self {
        Self(value.to_string())
    }
}

impl From<Utf8Error> for TesserocrError {
    fn from(value: Utf8Error) -> Self {
        Self(value.to_string())
    }
}

impl From<NulError> for TesserocrError {
    fn from(value: NulError) -> Self {
        Self(value.to_string())
    }
}

impl From<TessInitError> for TesserocrError {
    fn from(value: TessInitError) -> Self {
        Self(value.to_string())
    }
}

impl ToOwned for TesserocrError {
    type Owned = Self;

    fn to_owned(&self) -> Self::Owned {
        Self(self.0.clone())
    }
}

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
    fn new(
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

    fn init(&mut self) -> PyResult<()> {
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
                        let ret =  tess_api
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

    fn ocr(&mut self, images: Vec<Option<PyReadonlyArray<u8, Ix3>>>, config: Option<&str>) -> PyResult<Vec<Option<String>>> {
        let blacklist = extract_blacklist(config)?;

        let images: Vec<_> = images
            .into_iter()
            .map(|option| option
                .map(|image| {
                    let shape = image.shape();
                    let (height, width) = if let &[a, b, 3] = shape {
                        (a as u32, b as u32)
                    } else {
                        panic!("invalid for rgb image, expected [_, _, 3] but got {:?}", shape)
                    };

                    image.to_vec()
                        .map(|image| (image, width, height))
                        .map_err(|_| r#"invalid layout, please make sure that the array data is in contiguous "C order""#.into())
                })
            )
            .map(|option| option.transpose())
            .collect::<Result<_, TesserocrError>>()?;


        if let Some(pool) = &mut self.pool {
            Ok(ocr(pool, images, blacklist)?)
        } else {
            Err(TesserocrError::from("Thread Pool is not initialized").into())
        }
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

fn ocr(pool: &mut ThreadPool,
       images: Vec<Option<(Vec<u8>, u32, u32)>>,
       blacklist: Option<&str>) -> Result<Vec<Option<String>>, TesserocrError> {
    fn ocr(image: Option<(Vec<u8>, u32, u32)>,
           blacklist: Option<&str>) -> Option<Result<String, TesserocrError>> {
        image.map(|(image, width, height)|
            TESS_API.with(|cell| {
                let mut tess_api = cell.take().unwrap();

                let ret = match blacklist {
                    Some(blacklist) =>
                        tess_api.set_variable("tesseract_char_blacklist", blacklist)
                            .and_then(|_| tess_api.ocr(&image, width, height)),
                    None => tess_api.ocr(&image, width, height),
                };

                cell.set(Some(tess_api));

                ret
            })
        )
    }

    pool.scope(|_| images
        .into_par_iter()
        .map(|image| ocr(image, blacklist))
        .map(|x| x.transpose())
        .collect()
    )
}

#[pymodule]
fn tesserocr_pool(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_class::<TesserocrPool>()?;

    Ok(())
}

thread_local! {
    static TESS_API: Cell<Option<TessApi>> = Cell::new(None);
}