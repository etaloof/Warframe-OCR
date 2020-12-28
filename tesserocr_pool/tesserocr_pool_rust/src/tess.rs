use std::convert::TryInto;
use std::ffi::{CStr, CString, NulError};
use std::fmt::{Display, Formatter};
use std::ops::Deref;
use std::os::raw::c_char;
use std::ptr;

use leptess::capi;
use leptess::leptonica;
use leptess::tesseract::*;
use leptonica::*;

use crate::TesserocrError;

fn bgr_to_rgb(mut image: Vec<u8>) -> Vec<u8> {
    assert_eq!(image.len() % 3, 0, "bgr image must have an integer number of pixels");
    for pixel in image.chunks_exact_mut(3) {
        if let [b, _g, r] = pixel {
            std::mem::swap(b, r);
        } else {
            panic!("chunks should have length of 3 but got length {}", pixel.len());
        }
    }

    image
}

fn rgb_to_bmp(image: &[u8], width: u32, height: u32) -> Vec<u8> {
    let mut buffer = Vec::with_capacity(image.len());

    let _ = image::codecs::bmp::BmpEncoder::new(&mut buffer)
        .encode(image, width, height, image::ColorType::Rgb8)
        .unwrap();

    buffer
}

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
    pub fn new(data_path: Option<&str>, lang: &str) -> Result<TessApi, TesserocrError> {
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
        unsafe { capi::TessBaseAPISetImage2(self.raw, img.raw as *mut capi::Pix) }
    }

    pub fn set_image_from_mem(&mut self, img: &[u8], width: u32, height: u32) -> Result<(), TesserocrError> {
        // convert from bgr to rgb and then to bmp
        // because why not
        let img = img.to_vec();
        let img = bgr_to_rgb(img);
        let img = rgb_to_bmp(&img, width, height);

        let pix = pix_read_mem_bmp(&img)?;
        self.set_image(&pix);
        Ok(())
    }

    pub fn ocr(&mut self, img: &[u8], width: u32, height: u32) -> Result<String, TesserocrError> {
        unsafe {
            capi::TessBaseAPISetPageSegMode(self.raw, capi::TessPageSegMode_PSM_SINGLE_BLOCK);
        }

        self.set_image_from_mem(img, width, height)?;
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
pub struct TessString(pub *mut c_char);

impl TessString {
    pub fn new(string: &str) -> Result<Self, NulError> {
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

// leptonica error messages are max 2000 bytes long
// leave one byte as null terminator
struct ErrorMessage([c_char; 2000 + 1]);

impl AsRef<CStr> for ErrorMessage {
    fn as_ref(&self) -> &CStr {
        assert_eq!(*self.0.last().unwrap(), 0);

        // this is safe because
        // - self.0.as_ptr() can not be null
        // - the last byte of the array is always 0
        unsafe { CStr::from_ptr(self.0.as_ptr()) }
    }
}

pub fn pix_read_mem_bmp(img: &[u8]) -> Result<Pix, PixError> {
    let img_len = img.len().try_into()?;
    let pix = unsafe {
        capi::pixReadMemBmp(img.as_ptr(), img_len)
    };
    if pix.is_null() {
        Err(PixError::ReadFrom("memory"))
    } else {
        Ok(Pix { raw: pix })
    }
}