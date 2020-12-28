use std::error::Error;
use std::ffi::NulError;
use std::fmt;
use std::str::Utf8Error;

use leptess::leptonica::PixError;
use leptess::tesseract::TessInitError;
use pyo3::PyErr;
use rayon::{
    ThreadPoolBuildError,
};


pub mod tess;

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
