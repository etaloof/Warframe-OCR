// Source adopted from
// https://github.com/tildeio/helix-website/blob/master/crates/word_count/src/lib.rs

use std::fmt;
use std::ops::DerefMut;

use pyo3::{
    prelude::*,
    wrap_pyfunction,
    types::PyType,
};
use rayon::{
    prelude::*,
    ThreadPool,
    ThreadPoolBuilder,
    ThreadPoolBuildError,
};
use pyo3::types::PyDict;

/// Searches for the word, parallelized by rayon
#[pyfunction]
fn search(contents: &str, needle: &str) -> usize {
    contents
        .par_lines()
        .map(|line| count_line(line, needle))
        .sum()
}

/// Searches for a word in a classic sequential fashion
#[pyfunction]
fn search_sequential(contents: &str, needle: &str) -> usize {
    contents.lines().map(|line| count_line(line, needle)).sum()
}

#[pyfunction]
fn search_sequential_allow_threads(py: Python, contents: &str, needle: &str) -> usize {
    py.allow_threads(|| search_sequential(contents, needle))
}

fn matches(word: &str, needle: &str) -> bool {
    let mut needle = needle.chars();
    for ch in word.chars().skip_while(|ch| !ch.is_alphabetic()) {
        match needle.next() {
            None => {
                return !ch.is_alphabetic();
            }
            Some(expect) => {
                if ch.to_lowercase().next() != Some(expect) {
                    return false;
                }
            }
        }
    }
    needle.next().is_none()
}

/// Count the occurences of needle in line, case insensitive
fn count_line(line: &str, needle: &str) -> usize {
    let mut total = 0;
    for word in line.split(' ') {
        if matches(word, needle) {
            total += 1;
        }
    }
    total
}

const SETUP_THREAD: &str =
    r#"
import tesserocr
tessdata_dir = 'tessdata/'
tess = PyTessBaseAPI(tessdata_dir, 'Roboto', psm=PSM.SINGLE_BLOCK, oem=OEM.LSTM_ONLY)
"#;

const CLEAR_THREAD: &str =
    r#"
tess.End()
"#;

const OCR: &str =
    r#"
if "blacklist" in config:
    *_, config = config.split(" ")
_, config = config.split("=")

tess.SetVariable("tesseract_char_blacklist", config)

image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
image = Image.fromarray(image)

tess.SetImage(image)

text = tess.GetUTF8Text()

if "blacklist" in config:
    tess.SetVariable("tesseract_char_blacklist", None)
"#;

struct TesserocrError(String);

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

impl From<TesserocrError> for PyErr {
    fn from(value: TesserocrError) -> Self {
        value.into()
    }
}

#[pyclass]
#[derive(Debug)]
struct TesserocrPool {
    pool: Option<ThreadPool>
}

#[pymethods]
impl TesserocrPool {
    #[new]
    fn new() -> PyResult<Self> {
        let pool = None;
        Ok(Self { pool })
    }

    fn cleanup(&mut self) {
        let _ = self.pool.take();
    }

    fn init(&mut self) -> PyResult<()> {
        if self.pool.is_none() {
            self.pool = ThreadPoolBuilder::new()
                .start_handler(|arg| {
                    use leptess::tesseract::*;
                    thread_local! {
                        static TESS_API: Result<TessApi, TessInitError> = TessApi::new(Some("tessdata/"), "Roboto");
                    }
                    let x = TESS_API.with(|x| format!("{:?}",x));
                    println!("starting thread with arg: {} = {}", arg, x)
                })
                .build()
                .map_err(|err| TesserocrError::from(err))?
                .into();
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

    fn ocr(self_: PyRefMut<Self>, config: &str, image: &PyAny) -> PyResult<()> {
        if config.contains("blacklist") {}
        let locals = PyDict::new(self_.py());
        locals.set_item("image", image)?;
        locals.set_item("config", config)?;

        self_.py().run(OCR, None, Some(locals))
    }
}

#[pymodule]
fn tesserocr_pool(_py: Python<'_>, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(search, m)?)?;
    m.add_function(wrap_pyfunction!(search_sequential, m)?)?;
    m.add_function(wrap_pyfunction!(search_sequential_allow_threads, m)?)?;
    m.add_class::<TesserocrPool>()?;

    Ok(())
}


mod tess {
    use std::str::Utf8Error;
    use std::error::Error;
    use leptess::tesseract::*;
    use leptess::leptonica;

    pub fn set_blacklist(tess_api: &mut TessApi, blacklist: &str) {

    }

    pub fn ocr(tess_api: &mut TessApi, image: &[u8], blacklist: Option<&str>) -> Result<String, Box<dyn Error>> {
        set_image_from_mem(tess_api,image)?;
        tess_api.raw;
        Ok(tess_api.get_utf8_text()?)
    }

    pub fn set_image_from_mem(tess_api: &mut TessApi, img: &[u8]) -> Result<(), leptonica::PixError> {
        let pix = leptonica::pix_read_mem(img)?;
        tess_api.set_image(&pix);
        Ok(())
    }
}