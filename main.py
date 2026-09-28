import sys
import os
import subprocess
import yt_dlp
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, 
                               QPushButton, QLabel, QHBoxLayout, QLineEdit, 
                               QComboBox, QStackedWidget, QFrame, QFileDialog, 
                               QRadioButton, QButtonGroup, QSizePolicy)
from PySide6.QtCore import Qt, QThread, Signal
import PySide6.QtGui as QtGui

# /boost

def garantir_motor(signal_fim):
    import os, urllib.request, zipfile, shutil
    base = os.path.expanduser('~/.eto_media')
    os.makedirs(base, exist_ok=True)
    ffmpeg_exe = os.path.join(base, 'ffmpeg.exe')
    ffprobe_exe = os.path.join(base, 'ffprobe.exe')
    
    if not os.path.exists(ffmpeg_exe) or not os.path.exists(ffprobe_exe):
        if signal_fim:
            signal_fim.emit("baixando motor...")
        zip_path = os.path.join(base, 'motor.zip')
        
        req = urllib.request.Request(
            'https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip',
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req) as resp, open(zip_path, 'wb') as f:
            shutil.copyfileobj(resp, f)
            
        with zipfile.ZipFile(zip_path, 'r') as z:
            for info in z.infolist():
                if info.filename.endswith('ffmpeg.exe'):
                    with z.open(info) as fonte, open(ffmpeg_exe, 'wb') as dest:
                        shutil.copyfileobj(fonte, dest)
                elif info.filename.endswith('ffprobe.exe'):
                    with z.open(info) as fonte, open(ffprobe_exe, 'wb') as dest:
                        shutil.copyfileobj(fonte, dest)
        try:
            os.remove(zip_path)
        except:
            pass
            
    return ffmpeg_exe, ffprobe_exe

class fundo_widget(QWidget):
    # /boost
    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide6.QtGui import QPixmap
        self.pix = QPixmap("C:/Users/yagol/.gemini/antigravity/brain/865ead90-80bc-4dc9-82d3-5c742bbe1d26/.user_uploaded/media_1790566061754.png")

    def paintEvent(self, event):
        from PySide6.QtGui import QPainter
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.GlobalColor.black)
        if hasattr(self, 'pix') and not self.pix.isNull():
            pix = self.pix.scaled(self.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            x = self.width() - pix.width()
            y = (self.height() - pix.height()) // 2
            painter.drawPixmap(x, y, pix)

# thread yt-dlp baixar
class thread_baixar(QThread):
    # /boost
    fim = Signal(str)
    
    def __init__(self, link, qual, is_audio, destino):
        super().__init__()
        self.link = link
        self.qual = qual
        self.is_audio = is_audio
        self.destino = destino
        
    def run(self):
        try:
            import os
            import subprocess
            
            ffmpeg_exe, ffprobe_exe = garantir_motor(self.fim)
            
            alvo_link = self.link
            if "spotify.com" in alvo_link:
                try:
                    import urllib.request, json
                    url_req = f"https://open.spotify.com/oembed?url={alvo_link}"
                    req = urllib.request.Request(url_req, headers={'User-Agent': 'Mozilla/5.0'})
                    html = urllib.request.urlopen(req).read().decode('utf-8')
                    titulo = json.loads(html).get('title', '')
                    if titulo:
                        alvo_link = f"ytsearch1:{titulo}"
                    else:
                        self.fim.emit("erro: spotify sem titulo")
                        return
                except Exception as e:
                    self.fim.emit(f"erro spotify: {str(e)[:30]}".lower())
                    return

            ydl_opts = {
                'outtmpl': os.path.join(self.destino, '%(title)s.%(ext)s'),
                'noplaylist': True,
                'quiet': True,
                'ffmpeg_location': ffmpeg_exe,
            }
            if self.is_audio:
                qual_kbps = self.qual.split("kbps")[0].strip()
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': qual_kbps,
                    }],
                })
            else:
                if "4k" in self.qual:
                    res = "2160"
                else:
                    res = self.qual.split("p")[0].strip()
                    
                ydl_opts.update({
                    'format': f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                })
                
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([alvo_link])
            self.fim.emit("pronto")
        except Exception as e:
            self.fim.emit(f"erro: {str(e)[:40]}".lower())

# thread ffmpeg converter
class thread_converter(QThread):
    # /boost
    fim = Signal(str)
    
    def __init__(self, arq, fmt, qual, destino):
        super().__init__()
        self.arq = arq
        self.fmt = fmt
        self.qual = qual
        self.destino = destino
        
    def run(self):
        try:
            import os
            import subprocess
            ffmpeg_exe, _ = garantir_motor(self.fim)
            
            saida = self.destino
            cmd = [ffmpeg_exe, '-y', '-i', self.arq]
            
            if self.fmt in ['mp4', 'mkv', 'webm', 'mov', 'avi']:
                if "18" in self.qual:
                    cmd.extend(['-crf', '18'])
                elif "35" in self.qual:
                    cmd.extend(['-crf', '35'])
                else:
                    cmd.extend(['-crf', '23'])
            elif self.fmt == 'mp3':
                cmd.extend(['-q:a', '2'])
            elif self.fmt in ['wav', 'flac']:
                pass
            elif self.fmt == 'webp':
                pass
                
            cmd.append(saida)
            flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0) if os.name == 'nt' else 0
            
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
            self.fim.emit("pronto")
                
        except Exception as e:
            self.fim.emit(f"erro: {str(e)[:40]}".lower())

# thread ffmpeg comprimir
class thread_comprimir(QThread):
    # /boost
    fim = Signal(str)
    
    def __init__(self, arq, peso, qual, destino):
        super().__init__()
        self.arq = arq
        self.peso = peso
        self.qual = qual
        self.destino = destino
        
    def run(self):
        try:
            import os
            import subprocess
            ffmpeg_exe, ffprobe_exe = garantir_motor(self.fim)
            
            saida = self.destino
            
            flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0) if os.name == 'nt' else 0
            
            try:
                proc = subprocess.run([ffprobe_exe, '-v', 'error', '-show_entries', 
                                       'format=duration', '-of', 
                                       'default=noprint_wrappers=1:nokey=1', self.arq], 
                                      capture_output=True, text=True, creationflags=flags)
                dur = float(proc.stdout.strip())
            except Exception as e:
                dur = 60.0
                
            alvo_mb = float(self.peso.split('mb')[0].strip())
            alvo_kbits = alvo_mb * 8192
            
            bitrate_v = max(10, int((alvo_kbits / dur) - 128))
            
            preset = "medium"
            if "slow" in self.qual:
                preset = "slow"
            elif "ultrafast" in self.qual:
                preset = "ultrafast"
            
            cmd = [
                ffmpeg_exe, '-y', '-i', self.arq,
                '-b:v', f'{bitrate_v}k',
                '-maxrate', f'{int(bitrate_v * 1.5)}k',
                '-bufsize', f'{int(bitrate_v * 2)}k',
                '-b:a', '128k',
                '-preset', preset,
                saida
            ]
            
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=flags)
            self.fim.emit("pronto")
                
        except Exception as e:
            self.fim.emit(f"erro: {str(e)[:40]}".lower())

class eto_app(QMainWindow):
    # /boost
    def __init__(self):
        super().__init__()
        
        # janela sem borda
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(500, 400)
        
        # fundo escuro
        self.cen = fundo_widget(self)
        self.cen.setStyleSheet("""
            QWidget {
                color: #dcdcdc;
                font-family: 'Chiller', 'Impact', 'Courier';
                font-size: 14px;
            }
            QPushButton {
                background-color: #030303;
                border: 1px solid #dcdcdc;
                padding: 4px;
            }
            QPushButton:hover {
                background-color: #dcdcdc;
                color: #030303;
            }
            QLineEdit, QComboBox {
                background-color: #080808;
                border: 1px solid #333;
                padding: 4px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.setCentralWidget(self.cen)
        
        # layout geral
        self.lay = QVBoxLayout(self.cen)
        self.lay.setContentsMargins(10, 10, 10, 10)
        self.lay.setSpacing(10)
        
        # barra topo
        self.topo = QHBoxLayout()
        self.lay.addLayout(self.topo)
        
        self.lbl_nome = QLabel("eto")
        self.lbl_nome.setStyleSheet("font-weight: bold; font-size: 16px;")
        self.topo.addWidget(self.lbl_nome)
        
        self.topo.addStretch()
        
        self.btn_min = QPushButton("-")
        self.btn_min.setFixedSize(25, 25)
        self.btn_min.clicked.connect(self.showMinimized)
        
        self.btn_fecha = QPushButton("x")
        self.btn_fecha.setFixedSize(25, 25)
        self.btn_fecha.clicked.connect(self.close)
        
        self.topo.addWidget(self.btn_min)
        self.topo.addWidget(self.btn_fecha)
        
        # ataduras
        self.lay.addWidget(self.cria_faixa())
        self.lay.addWidget(self.cria_faixa())
        
        # botoes
        self.menu = QHBoxLayout()
        self.lay.addLayout(self.menu)
        
        self.btn_baixar = QPushButton("baixar")
        self.btn_converter = QPushButton("converter")
        self.btn_comprimir = QPushButton("comprimir")
        
        self.menu.addWidget(self.btn_baixar)
        self.menu.addWidget(self.btn_converter)
        self.menu.addWidget(self.btn_comprimir)
        
        self.lay.addWidget(self.cria_faixa())
        
        # abas
        self.telas = QStackedWidget()
        self.lay.addWidget(self.telas)
        
        self.telas.addWidget(self.tela_baixar())
        self.telas.addWidget(self.tela_converter())
        self.telas.addWidget(self.tela_comprimir())
        
        self.btn_baixar.clicked.connect(lambda: self.telas.setCurrentIndex(0))
        self.btn_converter.clicked.connect(lambda: self.telas.setCurrentIndex(1))
        self.btn_comprimir.clicked.connect(lambda: self.telas.setCurrentIndex(2))
        
        self.lay.addWidget(self.cria_faixa())
        
        # status e marca d'agua
        bot_lay = QHBoxLayout()
        
        spacer1 = QWidget()
        spacer1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        bot_lay.addWidget(spacer1)
        
        self.lbl_status = QLabel("pronto")
        self.lbl_status.setAlignment(Qt.AlignCenter)
        bot_lay.addWidget(self.lbl_status)
        
        spacer2 = QWidget()
        spacer2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        bot_lay.addWidget(spacer2)
        
        self.lbl_y3levi = QLabel("made by y3levi")
        self.lbl_y3levi.setStyleSheet("font-family: 'Courier'; font-size: 10px; color: #555; background: transparent;")
        bot_lay.addWidget(self.lbl_y3levi)
        
        self.lay.addLayout(bot_lay)

    # linha branca
    def cria_faixa(self):
        f = QFrame()
        f.setFixedHeight(1)
        f.setStyleSheet("background-color: #dcdcdc;")
        return f

    def buscar_arq(self, le):
        arq, _ = QFileDialog.getOpenFileName(self, "selecionar arquivo")
        if arq:
            le.setText(arq)

    # baixar
    def tela_baixar(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        self.link = QLineEdit()
        self.link.setPlaceholderText("link")
        l.addWidget(self.link)
        
        self.tipo_baixar = QButtonGroup(self)
        self.rad_video = QRadioButton("vídeo")
        self.rad_audio = QRadioButton("áudio")
        self.rad_video.setChecked(True)
        self.tipo_baixar.addButton(self.rad_video)
        self.tipo_baixar.addButton(self.rad_audio)
        
        hbox = QHBoxLayout()
        hbox.addWidget(self.rad_video)
        hbox.addWidget(self.rad_audio)
        l.addLayout(hbox)
        
        self.qual_baixar = QComboBox()
        self.muda_qual_baixar()
        l.addWidget(self.qual_baixar)
        
        self.rad_video.toggled.connect(self.muda_qual_baixar)
        self.rad_audio.toggled.connect(self.muda_qual_baixar)
        
        self.btn_vai_baixar = QPushButton("vai")
        self.btn_vai_baixar.clicked.connect(self.acao_baixar)
        l.addWidget(self.btn_vai_baixar)
        l.addStretch()
        return w

    def muda_qual_baixar(self):
        self.qual_baixar.clear()
        if self.rad_video.isChecked():
            self.qual_baixar.addItems(["4k - braba", "1080p - ok", "720p - de boa", "480p - podre"])
        else:
            self.qual_baixar.addItems(["320kbps - super braba", "192kbps - braba", "128kbps - ok", "64kbps - podre"])

    def acao_baixar(self):
        if not self.link.text(): return
        destino = QFileDialog.getExistingDirectory(self, "selecionar pasta de destino")
        if not destino:
            return
        self.lbl_status.setText("baixando...")
        self.btn_vai_baixar.setDisabled(True)
        self.th_baixar = thread_baixar(self.link.text(), self.qual_baixar.currentText(), self.rad_audio.isChecked(), destino)
        self.th_baixar.fim.connect(self.fim_acao)
        self.th_baixar.start()

    # converter
    def tela_converter(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        hb = QHBoxLayout()
        self.arq_converter = QLineEdit()
        self.arq_converter.setPlaceholderText("arquivo")
        self.btn_buscar_conv = QPushButton("...")
        self.btn_buscar_conv.setFixedWidth(30)
        self.btn_buscar_conv.clicked.connect(lambda: self.buscar_arq(self.arq_converter))
        hb.addWidget(self.arq_converter)
        hb.addWidget(self.btn_buscar_conv)
        l.addLayout(hb)
        
        self.fmt = QComboBox()
        self.fmt.addItems(["mp4", "mkv", "webm", "mp3", "mov", "gif", "webp", "wav", "flac", "avi"])
        l.addWidget(self.fmt)
        
        self.qual_converter = QComboBox()
        self.qual_converter.addItems(["18 crf - braba", "23 crf - ok", "35 crf - podre"])
        l.addWidget(self.qual_converter)
        
        self.btn_vai_converter = QPushButton("vai")
        self.btn_vai_converter.clicked.connect(self.acao_converter)
        l.addWidget(self.btn_vai_converter)
        l.addStretch()
        return w

    def acao_converter(self):
        arq = self.arq_converter.text()
        if not arq: return
        fmt = self.fmt.currentText()
        nome, _ = os.path.splitext(os.path.basename(arq))
        sugestao = os.path.join(os.path.dirname(arq), f"{nome}_convertido.{fmt}")
        destino, _ = QFileDialog.getSaveFileName(self, "salvar como", sugestao, f"arquivos {fmt} (*.{fmt})")
        if not destino:
            return
        self.lbl_status.setText("convertendo...")
        self.btn_vai_converter.setDisabled(True)
        self.th_converter = thread_converter(arq, fmt, self.qual_converter.currentText(), destino)
        self.th_converter.fim.connect(self.fim_acao)
        self.th_converter.start()

    # comprimir
    def tela_comprimir(self):
        w = QWidget()
        l = QVBoxLayout(w)
        
        hb = QHBoxLayout()
        self.arq_comprimir = QLineEdit()
        self.arq_comprimir.setPlaceholderText("arquivo")
        self.btn_buscar_comp = QPushButton("...")
        self.btn_buscar_comp.setFixedWidth(30)
        self.btn_buscar_comp.clicked.connect(lambda: self.buscar_arq(self.arq_comprimir))
        hb.addWidget(self.arq_comprimir)
        hb.addWidget(self.btn_buscar_comp)
        l.addLayout(hb)
        
        self.peso = QComboBox()
        self.peso.addItems(["8mb - braba", "25mb - ok", "50mb - podre"])
        l.addWidget(self.peso)
        
        self.qual_comprimir = QComboBox()
        self.qual_comprimir.addItems(["slow - braba", "medium - ok", "ultrafast - podre"])
        l.addWidget(self.qual_comprimir)
        
        self.btn_vai_comprimir = QPushButton("vai")
        self.btn_vai_comprimir.clicked.connect(self.acao_comprimir)
        l.addWidget(self.btn_vai_comprimir)
        l.addStretch()
        return w

    def acao_comprimir(self):
        arq = self.arq_comprimir.text()
        if not arq: return
        nome, ext = os.path.splitext(os.path.basename(arq))
        if not ext: ext = ".mp4"
        sugestao = os.path.join(os.path.dirname(arq), f"{nome}_comprimido{ext}")
        destino, _ = QFileDialog.getSaveFileName(self, "salvar como", sugestao, f"arquivos de vídeo (*{ext})")
        if not destino:
            return
        self.lbl_status.setText("comprimindo...")
        self.btn_vai_comprimir.setDisabled(True)
        self.th_comprimir = thread_comprimir(arq, self.peso.currentText(), self.qual_comprimir.currentText(), destino)
        self.th_comprimir.fim.connect(self.fim_acao)
        self.th_comprimir.start()

    def fim_acao(self, msg):
        self.lbl_status.setText(msg)
        if msg != "baixando motor...":
            if hasattr(self, 'btn_vai_baixar'): self.btn_vai_baixar.setEnabled(True)
            if hasattr(self, 'btn_vai_converter'): self.btn_vai_converter.setEnabled(True)
            if hasattr(self, 'btn_vai_comprimir'): self.btn_vai_comprimir.setEnabled(True)

    # para mover e redimensionar nas bordas
    def nativeEvent(self, eventType, message):
        if os.name == 'nt':
            try:
                from ctypes.wintypes import MSG
                msg = MSG.from_address(int(message))
                if msg.message == 0x0084: # wm_nchittest
                    x = msg.lParam & 0xffff
                    if x > 32767: x -= 65536
                    y = (msg.lParam >> 16) & 0xffff
                    if y > 32767: y -= 65536
                    
                    from PySide6.QtCore import QPoint
                    pos = self.mapFromGlobal(QPoint(x, y))
                    bx = pos.x()
                    by = pos.y()
                    w = self.width()
                    h = self.height()
                    
                    border = 8
                    is_top = by < border
                    is_bottom = by > h - border
                    is_left = bx < border
                    is_right = bx > w - border
                    
                    res = 0
                    if is_top and is_left: res = 13 # httopleft
                    elif is_top and is_right: res = 14 # httopright
                    elif is_bottom and is_left: res = 16 # htbottomleft
                    elif is_bottom and is_right: res = 17 # htbottomright
                    elif is_top: res = 12 # httop
                    elif is_bottom: res = 15 # htbottom
                    elif is_left: res = 10 # htleft
                    elif is_right: res = 11 # htright
                    elif by < 40: # caption
                        if bx > w - 80:
                            res = 1 # htclient (passa pros botoes)
                        else:
                            res = 2 # htcaption
                        
                    if res != 0:
                        return True, res
            except Exception as e:
                pass
        return super().nativeEvent(eventType, message)

# start
if __name__ == "__main__":
    app = QApplication(sys.argv)
    j = eto_app()
    j.show()
    sys.exit(app.exec())
