# Bản fork cá nhân

Fork của [toanbku/fmess](https://github.com/toanbku/fmess), chỉ để tự build dùng cá nhân.

Khác với bản gốc:

- **Tắt tự cập nhật** (commit `a804c7a`): app không tự tải và cài bản build của tác giả. Bản mới chỉ có khi tự merge từ tác giả và build lại.

Remote:

- `origin` là fork này (`khiconit/fmess`).
- `upstream` là repo tác giả, chỉ để fetch. Push đã bị chặn.

## Lấy bản mới từ tác giả

1. Tải thay đổi mới, chưa merge:

   ```bash
   git fetch upstream
   ```

2. Xem có những commit nào mới:

   ```bash
   git log --oneline main..upstream/main
   ```

3. Xem toàn bộ thay đổi code, bỏ qua file ảnh:

   ```bash
   git diff main...upstream/main -- . ':!*.png' ':!*.icns' ':!*.ico' ':!*.webp'
   ```

4. Kiểm tra bảo mật. Những chỗ cần đọc kỹ:
   - `src-tauri/src/inject.js`: script chạy trong trang Facebook. Tìm `fetch(`, `XMLHttpRequest`, `WebSocket`, `sendBeacon` và URL tới domain ngoài Facebook.
   - `src-tauri/capabilities/*.json`: những lệnh trang Facebook được phép gọi.
   - `src-tauri/Cargo.toml`, `package.json` và hai file lock: thư viện mới, thư viện lấy từ git thay vì crates.io hay npm.
   - `src-tauri/build.rs` và `src-tauri/src/*.rs`: tìm `Command`, `process::` và thao tác ghi xóa file.
   - `src-tauri/tauri.conf.json`: xem updater có bị bật lại không.

   Có thể nhờ Claude Code: "Review thay đổi từ upstream/main so với main về bảo mật".

5. Merge rồi build:

   ```bash
   git merge upstream/main
   ```

   Nếu xung đột ở các file updater (`main.rs`, `menu.rs`, `Cargo.toml`, `tauri.conf.json`), giữ phần đã tắt updater.

   ```bash
   cargo test --manifest-path src-tauri/Cargo.toml
   ```

   ```bash
   npm ci && npm run tauri build
   ```

6. Đẩy lên fork:

   ```bash
   git push origin main
   ```

App sau khi build nằm ở `src-tauri/target/release/bundle/` (`.app` và `.dmg`).
