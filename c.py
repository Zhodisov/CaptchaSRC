from flask import (
    Flask,
    Response,
    url_for,
    send_from_directory,
    request,
    jsonify,
    send_file,
    abort,
    render_template,
    render_template_string,
    redirect,
    session,
    Markup,
    make_response,
    flash,
)
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from itsdangerous import URLSafeTimedSerializer
import os
import json
import zipfile
from github import Github, UnknownObjectException, GithubException
import json
import base64
import tempfile
import io
import requests
from datetime import datetime, timedelta  
import stripe
import paypalrestsdk
import uuid
import logging
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import string
import numpy as np
import matplotlib.font_manager as fm
import math

app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)  

app.config[
    "SECRET_KEY"
] = b""
GITHUB_PAT = ""
REPO_NAME = ""
g = Github(GITHUB_PAT)
repo = g.get_user().get_repo(REPO_NAME)
def _grd():
    return (random.randint(32, 127), random.randint(32, 127), random.randint(32, 127))

def _log(ip, s, t, ur):
    data = {
        "IP": ip,
        "UserAgent": request.headers.get('User-Agent', 'Unknown'),
        "Captcha": t,
        "Reussi": s,
        "ReponseUtilisateur": ur,
        "DateHeure": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Essais": session.get('attempts', 0)
    }

    f_p = f"CAPTCHA/{ip}.json"
    try:
        sha = None  

        try:
            f = repo.get_contents(f_p)
            l = json.loads(base64.b64decode(f.content))
            sha = f.sha 
        except UnknownObjectException:
            l = []

        l.append(data)
        formatted_log_data = json.dumps(l, indent=4)

        if sha:
            repo.update_file(f_p, "CAPTCHA attempts log for IP " + ip, formatted_log_data, sha)
        else:
            repo.create_file(f_p, "IP log creation " + ip, formatted_log_data)
    except GithubException as e:
        app.logger.error(f"Error log for IP {ip}: {e}")
def _a_d_s_x(ip):
    f_p = f"/CAPTCHA/{ip}.json"
    try:
        f = repo.get_contents(f_p)
        l = json.loads(base64.b64decode(f.content))
        s_c = sum(d.get('Reussi', False) for d in l)
        a_c = len(l)
        s_r = s_c / a_c if a_c else 0
        if s_r > 0.9:
            d = 'simple'
        elif s_r > 0.75:
            d = 'easy'
        elif s_r > 0.6:
            d = 'medium'
        elif s_r > 0.45:
            d = 'hard'
        elif s_r > 0.3:
            d = 'difficult'
        else:
            d = 'hardcore'
        if a_c > 10 and s_r < 0.3:
            _u_b(ip, bl=True)

        return d
    except GithubException as e:
        return 'medium' 

def _u_b(i, bl=True):
    try:
        f = repo.get_contents("/CAPTCHA/blacklist.json")
        b = json.loads(base64.b64decode(f.content))
        if bl:
            if i not in b['blocked_ips']:
                b['blocked_ips'].append(i)
        else:
            if i in b['blocked_ips']:
                b['blocked_ips'].remove(i)
        repo.update_file(f.path, "Update", json.dumps(b), f.sha)
    except GithubException as e:
        app.logger.error(e)
def _g_i():
    x = request.headers.get('X-Forwarded-For')
    if x:
        u = x.split(",")[0].strip()
    else:
        u = request.remote_addr
    return u

class _C_G:
    def __init__(self, width=200, height=70, font_size=25):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.font_path = "Roboto-Black.ttf"
        self.dif = 'medium'
        self.distortion_level = 0.3
        self.background_color = (14, 14, 14)
        self.cad = (51, 206, 126)
        self.line_color = (51, 206, 126)
        self.sca = 5


    @staticmethod
    def _g_s(base_color):
        v = random.randint(-20, 20)
        return tuple(min(255, max(0, base_color[i] + v)) for i in range(3))
    def _a_dg(self, dr, coo):
        for x, y in coo:
            for i in range(-2, 3):
                for j in range(-2, 3):
                    if random.random() > 0.5:
                        dr.point((x + i, y + j), fill=self._g_rd())

    def _g_rd(self):

        return _C_G._g_s(self.cad)

    def _a_m(self, i):
        mo = 10
        for x in range(0, self.width, mo):
            for y in range(0, self.height, mo):
                self._d_m(i, x, y, mo)

    def _d_m(self, i, x, y, size):
        dr = ImageDraw.Draw(i)
        col = (*_grd(), 100)
        dr.rectangle([x, y, x + size, y + size], fill=col)

    def _a_n(self, dr, width, height, col):
        for _ in range(random.randint(100, 200)):
            x, y = random.randint(0, width), random.randint(0, height)
            dr.point((x, y), fill=_C_G._g_s(col))

    def _a_n_d(self, dr, width, height, col):
        for _ in range(random.randint(5, 10)):
            st = (random.randint(0, width), random.randint(0, height))
            en = (random.randint(0, width), random.randint(0, height))
            dr.line([st, en], fill=_C_G._g_s(col), width=2)

    def _a_d_i(self, i):
        w, h = i.size
        dx = w * random.uniform(0.1, 0.8)  
        dy = h * random.uniform(0.1, 0.8) 
        for i in range(h):
            for j in range(w):
                if i % 2 == 0:
                    i.putpixel((j, i), i.getpixel((min(w - 1, max(0, int(j + dx * np.sin(np.pi * i / h)))), i)))
                else:
                    i.putpixel((j, i), i.getpixel((min(w - 1, max(0, int(j + dy * np.sin(np.pi * j / w)))), i)))
        return i
    def _g_c_c(self, background_color):
        return tuple(255 - background_color[i] for i in range(3))

    def _d_s_t(self, dr, t, font, position):
        lec = []
        sca = 5
        x, y = position

        for i, char in enumerate(t):
            cx = x + (self.font_size + sca) * i
            cy = y 
            dr.t((cx, cy), char, fill=self.cad, font=font)

            cbbx = dr.textbbox((cx, cy), char, font=font)
            lcx = (cbbx[0] + cbbx[2]) / 2
            lcy = (cbbx[1] + cbbx[3]) / 2
            lec.append((lcx, lcy))

        return lec

    def _a_r_l(self, dr):
        for _ in range(5):
            st = (0, random.randint(0, self.height))
            en = (self.width, random.randint(0, self.height))
            dr.line([st, en], fill=_grd(), width=2)
    def _s_d_f(self, dif):
        self.dif = dif
        if dif == 'simple':
            self.font_size = 45
            self.distortion_level = 0.1
        elif dif == 'easy':
            self.font_size = 40
            self.distortion_level = 0.2
        elif dif == 'medium':
            self.font_size = 35
            self.distortion_level = 0.3
        elif dif == 'hard':
            self.font_size = 30
            self.distortion_level = 0.4
        elif dif == 'difficult':
            self.font_size = 25
            self.distortion_level = 0.5
        elif dif == 'hardcore':
            self.font_size = 20
            self.distortion_level = 0.6
    def _g_s_c(self):
        t = ''.join(random.choice([str.upper, str.lower])(char) for char in random.choices(string.ascii_letters + string.digits, k=6))
        i = Image.new('RGB', (self.width, self.height), self.background_color)
        dr = ImageDraw.Draw(i)
        font = ImageFont.truetype(self.font_path, self.font_size)
        self._d_b_l(dr, i.size, font)
        tw = sum(dr.textbbox((0, 0), char, font=font)[2] for char in t) + (len(t) - 1) * self.sca
        tx = (self.width - tw) // 2
        ty = (self.height - self.font_size) // 2
        coo = []
        for char in t:
            ox, oy = random.randint(-5, 5), random.randint(-5, 5)
            cx = tx + ox
            cy = ty + oy
            dr.t((cx, cy), char, fill=self.cad, font=font)
            bbox = dr.textbbox((cx, cy), char, font=font)
            lcxc = ((bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2)
            coo.append(lcxc)
            tx += dr.textbbox((0, 0), char, font=font)[2] + self.sca
        dr.line(coo, fill=self.line_color, width=3, joint=None)
        fte = "SafeMarket.xyz"
        ff = ImageFont.truetype(self.font_path, 10)
        ftb = dr.textbbox((0, self.height), fte, font=ff)
        dr.t((5, self.height - (ftb[3] - ftb[1]) - 5), fte, fill="white", font=ff)
        ib = io.BytesIO()
        i.save(ib, format='PNG')
        ib.seek(0)


        return t, ib
    def _d_b_l(self, dr, image_size, font):
        width, height = image_size
        for _ in range(30):
            char = random.choice(string.ascii_letters)
            cx = random.randint(0, width)
            cy = random.randint(0, height)
            dr.t((cx, cy), char, fill=(99, 100, 100), font=font)

cxax = _C_G()
@app.route("/")
def index():
    ct, cib = cxax._g_s_c()
    ci = cib.getvalue()
    ci64 = base64.b64encode(ci).decode('utf-8')
    cb = f"data:i/png;base64,{ci64}"
    session['captcha_text'] = ct
    session['captcha_generated_time'] = datetime.now().isoformat()
    return render_template("index.html", cb=cb)

@app.route('/verify', methods=['POST'])
def _vc():
    x = request.headers.get('X-Forwarded-For')
    u = x.split(",")[0].strip() if x else request.remote_addr
    ur = request.form['captcha_response']
    ciu = datetime.fromisoformat(session.get('captcha_generated_time', ''))

    if datetime.now() - ciu > timedelta(minutes=1):
        return redirect('/')

    a_cc = session.get('captcha_text', '')
    s = ur.lower() == a_cc.lower()

    _log(u, s, a_cc, ur)

    if s:
        session['attempts'] = 0
        return redirect('/')
    else:
        a = session.get('attempts', 0) + 1
        session['attempts'] = a

        d = _a_d_s_x(u)

        cxax._s_d_f(d)


        if a > 5:
            return redirect('/')
        else:
            return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
