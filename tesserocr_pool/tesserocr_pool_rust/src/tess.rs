use super::*;

use std::ops::{Deref, DerefMut};
use std::ffi::CString;
use std::fmt::{Debug, Formatter};

pub use leptess::LepTess;
use leptess::capi;

pub struct TessApi(LepTess);

impl Deref for TessApi {
    type Target = LepTess;

    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl DerefMut for TessApi {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

impl Debug for TessApi {
    fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
        self.0.as_raw_handle().fmt(f)
    }
}

impl TessApi {
    pub fn raw(&mut self) -> *mut capi::TessBaseAPI {
        self.0.as_raw_handle_mut().raw
    }

    pub fn new(data_path: Option<&str>, lang: &str) -> Result<TessApi, TesserocrError> {
        let lep_tess = LepTess::new(data_path, lang)?;
        Ok(Self(lep_tess))
    }

    pub fn ocr(&mut self, img: impl Into<Vec<u8>>, width: u32, height: u32) -> Result<String, TesserocrError> {
        unsafe {
            capi::TessBaseAPISetPageSegMode(self.raw(), capi::TessPageSegMode_PSM_SINGLE_BLOCK);
        }

        let img = img.into();
        let img = bgr_to_rgb(img);
        let img = rgb_to_bmp(&img, width, height);

        self.set_image_from_mem(&img)?;
        Ok(self.get_utf8_text()?)
    }

    pub fn set_variable(&mut self, key: &str, value: &str) -> Result<(), TesserocrError> {
        // maybe use a string pool to prevent leaking memory config variables
        let key = CString::new(key)?.into_raw();
        let value = CString::new(value)?.into_raw();
        unsafe {
            capi::TessBaseAPISetVariable(self.raw(), key, value);
        }

        Ok(())
    }
}

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
