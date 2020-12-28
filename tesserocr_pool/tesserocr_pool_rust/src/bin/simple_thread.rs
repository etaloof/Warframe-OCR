use std::cell::Cell;
use std::error::Error;
use std::ops::Deref;
use std::sync::{Arc, Barrier, Mutex};

use leptess::tesseract::{TessApi, TessInitError};
use rayon::{ThreadPool, ThreadPoolBuilder};
use rayon::prelude::*;

// use tesserocr_pool::tess::TessApi;
// use tesserocr_pool::TesserocrError;

thread_local! {
    static TESS_API43: Cell<Option<TessApi>> = Cell::new(None);
}


fn main() {
    let file = include_bytes!("../../../../test_images.bincode");
    let mut images: Vec<Option<(&[u8], u32, u32)>> = bincode::deserialize(file).unwrap();

    dbg!();

    let i = 1;
    init(i, "../tessdata/", "Roboto", 6, 1).unwrap();

    dbg!();
    // let blacklist = Some("tessedit_char_blacklist=jJyY");
    // let result = ocr(&mut pool, images, blacklist).unwrap();
    // dbg!(result);
}


pub fn init(arg: u32, tessdata_dir: impl Into<String>, lang: impl Into<String>, psm: u32, oem: u32) -> Result<(), Box<dyn Error>> {
    let tessdata_dir = &tessdata_dir.into();
    let lang = &lang.into();

    match TessApi::new(Some(tessdata_dir), lang) {
        Ok(_) => Ok(()),
        Err(err) => Err(Box::new(err)),
    }
}
