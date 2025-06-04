import gradio as gr
import pyautogui
import time
import threading
from PIL import Image
import io
import base64


class ScreenShare:
    def __init__(self):
        self.is_sharing = False
        self.current_screenshot = None
        self.update_interval = 1.0

    def capture_screen(self):
        try:
            screenshot = pyautogui.screenshot()
            screenshot = screenshot.resize((1280, 720), Image.Resampling.LANCZOS)

            return screenshot
        except Exception as e:
            print(f"截图失败: {e}")
            return None

    def start_sharing(self):
        self.is_sharing = True
        return "屏幕共享已开始"

    def stop_sharing(self):
        self.is_sharing = False
        return "屏幕共享已停止"

    def get_current_screen(self):
        if self.is_sharing:
            screenshot = self.capture_screen()
            if screenshot:
                return screenshot

        blank_image = Image.new('RGB', (1280, 720), color='black')
        return blank_image

    def set_update_interval(self, interval):
        self.update_interval = max(0.1, float(interval))
        return f"更新间隔已设置为 {self.update_interval} 秒"

screen_share = ScreenShare()

def create_interface():
    with gr.Blocks(title="屏幕共享", theme=gr.themes.Soft()) as demo:
        gr.Markdown("# 📱 电脑屏幕共享到手机")
        gr.Markdown("通过这个应用，你可以在手机上实时查看电脑屏幕内容")

        with gr.Row():
            with gr.Column(scale=2):
                screen_display = gr.Image(
                    label="电脑屏幕",
                    interactive=False,
                    show_download_button=False,
                    height=400
                )

                gr.HTML("""
                <script>
                function autoRefresh() {
                    const refreshButton = document.querySelector('button[id*="refresh"]');
                    if (refreshButton && window.screenShareActive) {
                        refreshButton.click();
                    }
                }

                // 每秒刷新一次
                setInterval(autoRefresh, 1000);
                window.screenShareActive = false;
                </script>
                """)

            with gr.Column(scale=1):
                gr.Markdown("### 控制面板")

                start_btn = gr.Button("🎬 开始共享", variant="primary")
                stop_btn = gr.Button("⏹️ 停止共享", variant="stop")
                refresh_btn = gr.Button("🔄 手动刷新", elem_id="refresh")

                # 设置更新间隔
                gr.Markdown("### 设置")
                interval_slider = gr.Slider(
                    minimum=0.1,
                    maximum=5.0,
                    value=1.0,
                    step=0.1,
                    label="刷新间隔（秒）"
                )

                # 状态显示
                status_text = gr.Textbox(
                    label="状态",
                    value="准备就绪",
                    interactive=False
                )

                # 说明文档
                gr.Markdown("""
                ### 使用说明
                1. 点击"开始共享"按钮
                2. 在手机浏览器中打开相同网址
                3. 屏幕会自动刷新显示电脑内容
                4. 可调整刷新间隔以平衡流畅度和性能

                ### 注意事项
                - 首次使用可能需要授权屏幕截图权限
                - 建议在同一网络环境下使用
                - 刷新间隔越短越流畅，但会增加CPU占用
                """)

        # 事件绑定
        start_btn.click(
            fn=lambda: (screen_share.start_sharing(), screen_share.get_current_screen()),
            outputs=[status_text, screen_display]
        ).then(
            fn=None,
            js="() => { window.screenShareActive = true; }"
        )

        stop_btn.click(
            fn=lambda: (screen_share.stop_sharing(), None),
            outputs=[status_text, screen_display]
        ).then(
            fn=None,
            js="() => { window.screenShareActive = false; }"
        )

        refresh_btn.click(
            fn=screen_share.get_current_screen,
            outputs=screen_display
        )

        interval_slider.change(
            fn=screen_share.set_update_interval,
            inputs=interval_slider,
            outputs=status_text
        )

    return demo


if __name__ == "__main__":
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    demo = create_interface()
    demo.launch(
        share=True
    )