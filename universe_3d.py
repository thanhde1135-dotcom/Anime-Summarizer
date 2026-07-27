import streamlit.components.v1 as components

def render_3d_universe():
    """Tạo không gian vũ trụ 3D vô cực siêu nhẹ bằng thuật toán toán học"""
    universe_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body, html {
                margin: 0;
                padding: 0;
                overflow: hidden;
                width: 100%;
                height: 100%;
                background-color: #000;
            }
            canvas {
                display: block;
            }
            .info-overlay {
                position: absolute;
                bottom: 20px;
                left: 20px;
                color: #00ffff;
                font-family: monospace;
                font-size: 14px;
                pointer-events: none;
                text-shadow: 0 0 5px rgba(0,255,255,0.7);
            }
        </style>
    </head>
    <body>
        <canvas id="spaceCanvas"></canvas>
        <div class="info-overlay">🌌 KHÔNG GIAN VŨ TRỤ 3D VÔ CỰC (Dung lượng: 0 KB - Sinh bằng thuật toán)</div>
        <script>
            const canvas = document.getElementById('spaceCanvas');
            const ctx = canvas.getContext('2d');

            function resize() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }
            window.addEventListener('resize', resize);
            resize();

            // Khởi tạo các vì sao trong không gian 3D ảo
            const stars = [];
            const numStars = 1000;
            const speed = 0.8;

            for (let i = 0; i < numStars; i++) {
                stars.push({
                    x: (Math.random() - 0.5) * canvas.width * 2,
                    y: (Math.random() - 0.5) * canvas.height * 2,
                    z: Math.random() * canvas.width,
                    size: Math.random() * 2.5
                });
            }

            function animate() {
                // Tạo hiệu ứng vệt sáng mờ ảo phía sau
                ctx.fillStyle = 'rgba(0, 0, 0, 0.25)';
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                const cx = canvas.width / 2;
                const cy = canvas.height / 2;

                for (let i = 0; i < stars.length; i++) {
                    let star = stars[i];
                    star.z -= speed;

                    // Nếu sao bay qua màn hình, tái tạo lại ở phía xa
                    if (star.z <= 0) {
                        star.z = canvas.width;
                        star.x = (Math.random() - 0.5) * canvas.width * 2;
                        star.y = (Math.random() - 0.5) * canvas.height * 2;
                    }

                    // Phép chiếu phối cảnh 3D (3D Projection)
                    let k = 300 / star.z;
                    let px = star.x * k + cx;
                    let py = star.y * k + cy;

                    if (px >= 0 && px <= canvas.width && py >= 0 && py <= canvas.height) {
                        let pSize = Math.max(0.5, star.size * k);
                        let alpha = Math.min(1, (canvas.width - star.z) / canvas.width);
                        
                        ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
                        ctx.beginPath();
                        ctx.arc(px, py, pSize, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
                requestAnimationFrame(animate);
            }
            animate();
        </script>
    </body>
    </html>
    """
    components.html(universe_html, height=600)
  
