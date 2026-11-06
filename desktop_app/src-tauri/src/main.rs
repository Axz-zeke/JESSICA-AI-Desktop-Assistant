#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            println!("Jessica Sovereign Desktop Initialized.");
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running jessica desktop application");
}

