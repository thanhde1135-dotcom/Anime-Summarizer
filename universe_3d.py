import streamlit.components.v1 as components

def render_3d_universe():
    """Không gian Sáng Tạo Đa Vũ Trụ: Từ Vũ Trụ Vô Cực đến Mạch Máu & Hệ Sinh Thái Sinh Học"""
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
                background-color: #020002;
                font-family: monospace;
            }
            canvas {
                display: block;
                cursor: crosshair;
            }
            .creator-panel {
                position: absolute;
                top: 20px;
                left: 20px;
                color: #ff3366;
                background: rgba(15, 0, 5, 0.9);
                padding: 18px;
                border: 2px solid #ff3366;
                border-radius: 10px;
                pointer-events: auto;
                box-shadow: 0 0 25px rgba(255,51,102,0.4);
                max-width: 340px;
            }
            .creator-panel h3 {
                margin-top: 0;
                color: #fff;
                text-shadow: 0 0 8px #ff3366;
            }
            button {
                background: #ff3366;
                color: #fff;
                border: none;
                padding: 8px 12px;
                margin: 5px 3px;
                cursor: pointer;
                font-weight: bold;
                border-radius: 5px;
                transition: 0.2s;
            }
            button:hover {
                background: #fff;
                color: #ff3366;
                box-shadow: 0 0 15px #ff3366;
            }
            .hint {
                font-size: 11px;
                color: #00ffcc;
                margin-top: 8px;
            }
        </style>
    </head>
    <body>
        <div class="creator-panel">
            <h3>🧬 ĐẤNG SÁNG TẠO ĐA VŨ TRỤ</h3>
            <p><b>Chọn thế giới bạn muốn tạo ra:</b></p>
            <button onclick="setMode('galaxy')">🌌 Vũ Trụ Sao</button>
            <button onclick="setMode('blood')">🩸 Mạch Máu & Tế Bào</button>
            <button onclick="setMode('neural')">🧠 Xung Điện Não</button>
            <button onclick="setMode('quantum')">⚛️ Lượng Tử Hỗn Mang</button>
            <div class="hint">💡 <i>Bấm chuột trái vào màn hình để sinh ra sự sống / thực thể tại đó!</i></div>
        </div>
        
        <canvas id="bioCanvas"></canvas>
        
        <script>
            const canvas = document.getElementById('bioCanvas');
            const ctx = canvas.getContext('2d');

            function resize() {
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }
            window.addEventListener('resize', resize);
            resize();

            let mode = 'blood'; // Mặc định mở lên là thế giới Mạch máu sinh học
            let particles = [];

            function setMode(newMode) {
                mode = newMode;
                initParticles();
            }

            class Entity {
                constructor(x, y, type) {
                    this.x = x;
                    this.y = y;
                    this.type = type;
                    this.vx = (Math.random() - 0.5) * 4;
                    this.vy = (Math.random() - 0.5) * 4;
                    this.radius = Math.random() * 6 + 2;
                    this.angle = Math.random() * Math.PI * 2;
                    this.life = 1.0;
                }

                update() {
                    if (mode === 'blood') {
                        // Hiệu ứng mạch máu: Dòng chảy co bóp theo nhịp tim
                        let heartbeat = Math.sin(Date.now() * 0.006) * 1.5;
                        this.x += this.vx + heartbeat;
                        this.y += this.vy;
                        if (this.x < 0) this.x = canvas.width;
                        if (this.x > canvas.width) this.x = 0;
                        if (this.y < 0) this.y = canvas.height;
                        if (this.y > canvas.height) this.y = 0;
                    } else if (mode === 'neural') {
                        // Hiệu ứng mạng lưới thần kinh phóng điện
                        this.x += this.vx * 0.5;
                        this.y += this.vy * 0.5;
                        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
                    } else {
                        this.x += this.vx;
                        this.y += this.vy;
                        if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
                        if (this.y < 0 || this.y > canvas.height) this.vy *= -1;
                    }
                }

                draw() {
                    ctx.beginPath();
                    if (mode === 'blood') {
                        // Tế bào máu / hồng cầu / bạch cầu
                        ctx.fillStyle = this.radius > 5 ? 'rgba(255, 50, 50, 0.85)' : 'rgba(200, 20, 20, 0.6)';
                        ctx.arc(this.x, this.y, this.radius * 1.5, 0, Math.PI * 2);
                        ctx.fill();
                        // Nhân tế bào
                        ctx.strokeStyle = '#ff9999';
                        ctx.lineWidth = 1;
                        ctx.stroke();
                    } else if (mode === 'neural') {
                        // Xung điện thần kinh
                        ctx.fillStyle = '#00ffcc';
                        ctx.arc(this.x, this.y, this.radius * 0.8, 0, Math.PI * 2);
                        ctx.fill();
                    } else {
                        // Vũ trụ sao
                        ctx.fillStyle = '#ffffff';
                        ctx.arc(this.x, this.y, this.radius * 0.6, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }
            }

            function initParticles() {
                particles = [];
                let count = 300;
                for (let i = 0; i < count; i++) {
                    particles.push(new Entity(Math.random() * canvas.width, Math.random() * canvas.height, mode));
                }
            }
            initParticles();

            // Bấm chuột để tạo ra bùng nổ tế bào hoặc xung điện mới tại chỗ
            window.addEventListener('click', (e) => {
                for(let i = 0; i < 30; i++) {
                    let p = new Entity(e.clientX, e.clientY, mode);
                    p.vx = (Math.random() - 0.5) * 8;
                    p.vy = (Math.random() - 0.5) * 8;
                    p.radius = Math.random() * 8 + 3;
                    particles.push(p);
                }
            });

            function animate() {
                // Tạo vệt mờ cho dòng chảy sinh học
                if (mode === 'blood') {
                    ctx.fillStyle = 'rgba(15, 2, 5, 0.25)';
                } else if (mode === 'neural') {
                    ctx.fillStyle = 'rgba(0, 10, 15, 0.25)';
                } else {
                    ctx.fillStyle = 'rgba(2, 0, 2, 0.25)';
                }
                ctx.fillRect(0, 0, canvas.width, canvas.height);

                // Vẽ các đường nối mạng lưới nếu là mạch máu hoặc thần kinh
                if (mode === 'blood' || mode === 'neural') {
                    for (let i = 0; i < particles.length; i++) {
                        for (let j = i + 1; j < particles.length; j++) {
                            let dx = particles[i].x - particles[j].x;
                            let dy = particles[i].y - particles[j].y;
                            let dist = Math.sqrt(dx * dx + dy * dy);
                            if (dist < 100) {
                                ctx.strokeStyle = mode === 'blood' ? `rgba(255, 0, 60, ${1 - dist/100})` : `rgba(0, 255, 204, ${1 - dist/100})`;
                                ctx.lineWidth = 0.8;
                                ctx.beginPath();
                                ctx.moveTo(particles[i].x, particles[i].y);
                                ctx.lineTo(particles[j].x, particles[j].y);
                                ctx.stroke();
                            }
                        }
                    }
                }

                particles.forEach(p => {
                    p.update();
                    p.draw();
                });

                requestAnimationFrame(animate);
            }
            animate();
        </script>
    </body>
    </html>
    """
    components.html(universe_html, height=700)
    
