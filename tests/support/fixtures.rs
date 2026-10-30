//! Accepted fixtures, read whether they are stored plain or gzip-compressed.
//!
//! The large prepared v2 fixtures are kept on disk as `NAME.gz`, written by `gzip -n` so the
//! bytes are reproducible. Tests and manifests still name `NAME`, and every accepted digest is
//! of the uncompressed bytes. `read` and `read_to_string` stand in for their `std::fs`
//! namesakes: they read `NAME` when it exists and otherwise decompress `NAME.gz`.
#![allow(dead_code)]

use std::{
    fs,
    io::{self, Read},
    path::{Path, PathBuf},
    sync::atomic::{AtomicUsize, Ordering},
};

fn compressed(path: &Path) -> PathBuf {
    let mut name = path.as_os_str().to_owned();
    name.push(".gz");
    PathBuf::from(name)
}

/// The bytes of `path`, or of its gzip copy when only that is stored.
pub fn read(path: impl AsRef<Path>) -> io::Result<Vec<u8>> {
    let path = path.as_ref();
    match fs::read(path) {
        Err(missing) if missing.kind() == io::ErrorKind::NotFound => {
            let Ok(file) = fs::File::open(compressed(path)) else {
                return Err(missing);
            };
            let mut bytes = Vec::new();
            flate2::read::GzDecoder::new(io::BufReader::new(file)).read_to_end(&mut bytes)?;
            Ok(bytes)
        }
        found => found,
    }
}

/// The text of `path`, or of its gzip copy when only that is stored.
pub fn read_to_string(path: impl AsRef<Path>) -> io::Result<String> {
    String::from_utf8(read(path)?)
        .map_err(|error| io::Error::new(io::ErrorKind::InvalidData, error))
}

/// A real file holding the bytes of `path`, for the engine binary to open: `path` itself when
/// it is stored plain, otherwise a copy decompressed into the system temporary folder.
pub fn file(path: impl AsRef<Path>) -> PathBuf {
    static NEXT: AtomicUsize = AtomicUsize::new(0);
    let path = path.as_ref();
    if path.is_file() {
        return path.to_path_buf();
    }
    let bytes = read(path).unwrap_or_else(|error| panic!("{}: {error}", path.display()));
    let directory = std::env::temp_dir().join(format!("forever-fixtures-{}", std::process::id()));
    fs::create_dir_all(&directory).unwrap();
    let name = path.file_name().unwrap().to_string_lossy();
    let target = directory.join(&*name);
    // Tests run side by side may want the same fixture: each writes its own copy and renames
    // it into place, so a reader never sees a partly written file.
    let partial = directory.join(format!("{name}.{}", NEXT.fetch_add(1, Ordering::Relaxed)));
    fs::write(&partial, bytes).unwrap();
    fs::rename(&partial, &target).unwrap();
    target
}
