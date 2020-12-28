use std::cell::{Cell, RefCell};
use std::error::Error;
use std::ops::Deref;
use std::sync::{Arc, Barrier, mpsc, Mutex};
use std::thread::JoinHandle;

use tesserocr_pool_rs as tesserocr_pool;
use tesserocr_pool::tess::TessApi;
use tesserocr_pool::TesserocrError;

thread_local! {
    static TESS_API42: Cell<Option<TessApi>> = Cell::new(None);
}


fn main() {
    let file = include_bytes!("../../../../test_images.bincode");
    let mut images: Vec<Option<(&[u8], u32, u32)>> = bincode::deserialize(file).unwrap();

    dbg!();

    {
        let (mut push, mut pop, mut pool) = init("../../tessdata/", "Roboto", 6, 1).unwrap();

        for image in &mut images {
            let image = image.take();
            push(None);
        }

        for handle in pool {
            handle.join().unwrap();
        }
    }



    //
    // images
    //     .map(|_| dispatcher_rx.recv().unwrap())
    //     .map(TesserocrError::from)
    //     .collect();


    dbg!();
    // let blacklist = Some("tessedit_char_blacklist=jJyY");
    // let result = ocr(&mut pool, images, blacklist).unwrap();
    // dbg!(result);
}

struct Task {
    id: u32,
    image: Option<(Vec<u8>, u32, u32)>,
    blacklist: Option<String>,
}

type TaskResult = (u32, Result<Option<String>, TesserocrError>);

fn init(
    tessdata_dir: impl Into<String>,
    lang: impl Into<String>,
    psm: u32,
    oem: u32,
) -> Result<(impl FnMut(Option<Task>) -> (), impl FnMut() -> TaskResult, Vec<JoinHandle<()>>), Box<dyn Error>> {
    let tessdata_dir = tessdata_dir.into();
    let lang = lang.into();

    let worker_count = num_cpus::get();
    // collect tesseract initialization results into a vector
    let results = Arc::new(Mutex::new(vec![]));
    // wait until all threads are ready
    let barrier = Arc::new(Barrier::new(worker_count + 1));

    let results_copy = results.clone();
    let barrier_copy = barrier.clone();

    let (mut dispatcher_tx, dispatcher_rx) = mpsc::channel();
    let (mut worker_tx, worker_rx) = spmc::channel();


    let mut handles = Vec::new();
    for n in 0..worker_count {
        let init = results_copy.clone();
        let barrier = barrier_copy.clone();
        let tessdata_dir = tessdata_dir.clone();
        let lang = lang.clone();
        let dispatcher_tx = dispatcher_tx.clone();
        let worker_rx = worker_rx.clone();
        handles.push(std::thread::spawn(move || {
            let result = {
                TessApi::new(Some(&tessdata_dir), &lang)
            };
            let result = match result {
                Ok(mut tess_api) => {
                    // let ret = tess_api
                    //     .set_variable("debug_file", "/dev/null")
                    //     .map(|_| format!("{:?}", &mut tess_api));

                    let ret = Ok(format!("{:?}", &mut tess_api));

                    TESS_API42.with(|tls|
                        tls.set(Some(tess_api))
                    );

                    ret
                }
                Err(err) => Err(err),
            };

            init
                .lock()
                .expect("Initialization result mutex shouldn't be poisoned")
                .push(dbg!((n, result)));

            dbg!(n);
            barrier.wait();

            loop {
                let result = match worker_rx.recv().expect("Broken channel: Is the dispacher thread gone?") {
                    Some(Task { id, image, blacklist }) => (id, ocr(image, blacklist.as_deref()).transpose()),
                    None => break,
                };

                dispatcher_tx.send(result);
            }
        }));
    }

    dbg!("main");
    barrier.wait();

    let mut guard = results.lock().unwrap();
    println!("thread count in thread pool is {}", guard.len());

    guard.sort_by_key(|&(n, _)| n);
    for (n, r) in guard.iter() {
        if let Err(err) = r {
            let err = format!("Thread {} failed to start: {}", n, err);
            Err(TesserocrError::from(err))?;
        }
    }


    Ok((
        move |task| worker_tx.send(task).unwrap(),
        move || dispatcher_rx.recv().unwrap(),
        handles
    ))
}

fn ocr(image: Option<(Vec<u8>, u32, u32)>,
       blacklist: Option<&str>) -> Option<Result<String, TesserocrError>> {
    image.map(|(image, width, height)|
        TESS_API42.with(|cell| {
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
