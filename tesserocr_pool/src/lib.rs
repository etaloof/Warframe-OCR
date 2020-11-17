// Source adopted from
// https://github.com/tildeio/helix-website/blob/master/crates/word_count/src/lib.rs

use std::fmt;
use std::ops::{DerefMut, Deref};

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
use ndarray::{ArrayD, ArrayViewD, ArrayViewMutD, Ix3};
use numpy::{IntoPyArray, PyArrayDyn, PyReadonlyArrayDyn, PyReadonlyArray};

use tess::TESS_API;
use leptess::leptonica::PixError;
use std::str::Utf8Error;
use std::ffi::NulError;
use leptess::tesseract::TessInitError;

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

#[derive(Debug)]
pub struct TesserocrError(String);

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
                    let x = TESS_API.with(|tls| {
                        let x = &mut tls.take().unwrap();
                        format!("{:?}", x)
                    });
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

    fn ocr(&mut self, images: Vec<Option<PyReadonlyArray<u8, Ix3>>>, config: Option<&str>) -> PyResult<Vec<Option<String>>> {
        let blacklist = match config {
            Some(config) if config.contains("blacklist") => {
                Some(
                    config.split(" ")
                        .last()
                        .ok_or(TesserocrError::from("invalid value for blacklist"))?
                        .split("=")
                        .last()
                        .ok_or(TesserocrError::from("invalid value for blacklist"))?
                )
            }
            _ => None,
        };

        let images: Vec<_> = images
            .iter()
            .map(|option|
                option.as_ref()
                    .map(|image|
                        image
                            .as_slice()
                            .map_err(|_| r#"invalid layout, please make sure that the array data is in contiguous "C order""#.into())
                    ).transpose()
            )
            .collect::<Result<_, TesserocrError>>()?;


        if let Some(pool) = &mut self.pool {
            Python::acquire_gil()
                .python()
                .allow_threads(||
                    Ok(ocr(pool, images, config)?)
                )
        } else {
            Err(TesserocrError::from("Thread Pool is not initialized").into())
        }
    }
}

fn ocr(pool: &mut ThreadPool,
       images: Vec<Option<&[u8]>>,
       blacklist: Option<&str>) -> Result<Vec<Option<String>>, TesserocrError> {
    pool.scope(|scope|
        images
            .into_par_iter()
            .map(|image: Option<&[u8]>|
                image.map(|image|
                    // we can initialize the thread locals better once
                    // https://github.com/rayon-rs/rayon/issues/493 lands
                    // until then storing a Result<TessApi, TessInitError> is necessary
                    // to implement correct error handling
                    TESS_API.with(|tls| {
                        // we are the only owner of the cell so we can simply unwrap
                        let x = &mut tls.take().unwrap();

                        match x {
                            Ok(x) => {
                                if let Some(blacklist) = blacklist {
                                    x.set_variable("tesseract_char_blacklist", blacklist)
                                        .and_then(|_| x.ocr(image))
                                } else {
                                    x.ocr(image)
                                }
                            }
                            Err(err) => Err(err.to_owned()),
                        }
                        // image.map(|x| x.ocr(image))
                    })
                ).transpose()
            )
            .collect()
    )
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
    use leptess::tesseract::*;
    use leptess::leptonica;
    use leptess::capi;
    use std::os::raw::c_char;
    use std::ffi::{CString, NulError, CStr};
    use std::ptr;
    use std::ops::Deref;
    use std::fmt::{Display, Formatter};
    use crate::TesserocrError;

    #[derive(Debug)]
    pub struct TessApi {
        pub raw: *mut capi::TessBaseAPI,
        pub data_path: TessString,
    }

    impl Drop for TessApi {
        fn drop(&mut self) {
            unsafe {
                capi::TessBaseAPIEnd(self.raw);
                capi::TessBaseAPIDelete(self.raw);
            }
        }
    }

    impl TessApi {
        pub fn new<'a>(data_path: Option<&'a str>, lang: &'a str) -> Result<TessApi, TesserocrError> {
            let data_path = TessString::from_option(data_path).unwrap();
            let lang = CString::new(lang).unwrap();

            let api = TessApi {
                raw: unsafe { capi::TessBaseAPICreate() },
                data_path,
            };

            unsafe {
                let re = capi::TessBaseAPIInit2(api.raw, *api.data_path, lang.as_ptr(), capi::TessOcrEngineMode_OEM_LSTM_ONLY);

                if re == 0 {
                    Ok(api)
                } else {
                    Err(TessInitError { code: re }.into())
                }
            }
        }

        /// Provide an image for Tesseract to recognize.
        ///
        /// set_image clears all recognition results, and sets the rectangle to the full image, so it
        /// may be followed immediately by a `[Self::get_utf8_text]`, and it will automatically perform
        /// recognition.
        pub fn set_image(&mut self, img: &leptonica::Pix) {
            // "Tesseract takes its own copy of the image, so it need not persist until after Recognize"
            unsafe { capi::TessBaseAPISetImage2(self.raw, img.raw as *mut capi::Pix) }
        }

        pub fn set_image_from_mem(&mut self, img: &[u8]) -> Result<(), TesserocrError> {
            let pix = leptonica::pix_read_mem(img)?;
            self.set_image(&pix);
            Ok(())
        }

        pub fn ocr(&mut self, img: &[u8]) -> Result<String, TesserocrError> {
            unsafe {
                capi::TessBaseAPISetPageSegMode(self.raw, capi::TessPageSegMode_PSM_SINGLE_BLOCK);
            }

            self.set_image_from_mem(img)?;
            Ok(self.get_utf8_text()?)
        }

        pub fn set_variable(&mut self, key: &str, value: &str) -> Result<(), TesserocrError> {
            // maybe use a string pool to prevent leaking memory config variables
            let key = CString::new(key)?.into_raw();
            let value = CString::new(value)?.into_raw();
            unsafe {
                capi::TessBaseAPISetVariable(self.raw, key, value);
            }

            Ok(())
        }

        pub fn get_utf8_text(&self) -> Result<String, std::str::Utf8Error> {
            unsafe {
                let re: Result<String, std::str::Utf8Error>;
                let sptr = capi::TessBaseAPIGetUTF8Text(self.raw);
                match CStr::from_ptr(sptr).to_str() {
                    Ok(s) => {
                        re = Ok(s.to_string());
                    }
                    Err(e) => {
                        re = Err(e);
                    }
                }
                capi::TessDeleteText(sptr);
                re
            }
        }
    }

    #[derive(Debug)]
    pub struct TessString(*mut c_char);

    impl TessString {
        fn new(string: &str) -> Result<Self, NulError> {
            Ok(Self(CString::new(string)?.into_raw()))
        }

        fn from_option(string: Option<&str>) -> Result<Self, NulError> {
            if let Some(string) = string {
                Self::new(string)
            } else {
                Ok(Self(ptr::null_mut()))
            }
        }
    }

    impl Drop for TessString {
        fn drop(&mut self) {
            unsafe {
                let &mut Self(string_ptr) = self;
                if !string_ptr.is_null() {
                    CString::from_raw(string_ptr);
                }
            }
        }
    }

    impl Deref for TessString {
        type Target = *mut c_char;

        fn deref(&self) -> &Self::Target {
            &self.0
        }
    }

    impl Display for TessString {
        fn fmt(&self, f: &mut Formatter<'_>) -> Result<(), std::fmt::Error> {
            if self.is_null() {
                return write!(f, "TessString{{NULL}}");
            }

            let s = unsafe {
                CStr::from_ptr(*self.deref()).to_str()
            };

            write!(f, "TessString{{{:?}}}", s)
        }
    }

    use std::cell::Cell;

    thread_local! {
        pub static TESS_API: Cell<Option<Result<TessApi, TesserocrError>>> =
            Cell::new(Some(TessApi::new(Some("tessdata/"), "Roboto")));
    }
}