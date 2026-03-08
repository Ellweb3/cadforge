"""
Генерация PDF планировок с размерами.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.backends.backend_pdf import PdfPages
import os


def build(output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "..")
    pdf_path = os.path.join(output_dir, "planimetrias.pdf")
    _generate(pdf_path)
    print("PDF saved: " + pdf_path)
    return pdf_path


def _dh(ax, x1, x2, y, text, off=0.3, fs=7):
    ax.annotate('', xy=(x2, y+off), xytext=(x1, y+off),
                arrowprops=dict(arrowstyle='<->', color='red', lw=0.8))
    ax.text((x1+x2)/2, y+off+0.15, text, ha='center', va='bottom',
            fontsize=fs, color='red')


def _dv(ax, x, y1, y2, text, off=0.3, fs=7):
    ax.annotate('', xy=(x+off, y2), xytext=(x+off, y1),
                arrowprops=dict(arrowstyle='<->', color='red', lw=0.8))
    ax.text(x+off+0.15, (y1+y2)/2, text, ha='left', va='center',
            fontsize=fs, color='red', rotation=90)


def _rm(ax, x, y, w, h, label, color='#f5f0e0'):
    ax.add_patch(Rectangle((x, y), w, h, fill=True, facecolor=color,
                            edgecolor='black', lw=1.2))
    ax.text(x+w/2, y+h/2, label, ha='center', va='center',
            fontsize=7, fontweight='bold')


def _page_main_house(pdf):
    WT = 0.15
    fig, ax = plt.subplots(1, 1, figsize=(11.69, 8.27))
    ax.set_aspect('equal')
    ax.set_title('PLAN \u2014 DOM 88 m\u00b2 (L-shape)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.add_patch(Rectangle((0, 7.6), 8.80, 4.40, fill=False,
                            edgecolor='black', lw=2.5))
    _rm(ax, WT, 7.6+WT, 8.80-2*WT, 4.40-2*WT,
        'ESTAR-COMEDOR\nCOCINA\n34.8 m\u00b2', '#e8dcc8')
    ax.add_patch(Rectangle((8.80, 0), 3.80, 12.00, fill=False,
                            edgecolor='black', lw=2.5))
    cw = 0.90
    rx = 8.80 + WT + cw
    rw = 3.80 - 2*WT - cw
    _rm(ax, 8.80+WT, WT, cw, 12.00-2*WT-3.30, 'PASILLO\n0.9 m', '#e0dcd0')
    d1y = 12.00 - WT - 3.30
    _rm(ax, 8.80+WT, d1y, 3.80-2*WT, 3.30,
        'DORM 1\n(master)\n11.6 m\u00b2', '#d4e8d4')
    b1y = d1y - 1.80
    _rm(ax, rx, b1y, rw, 1.80, 'BA\u00d1O 1\n4.7 m\u00b2', '#d4d8e8')
    b2y = b1y - 1.80
    _rm(ax, rx, b2y, rw, 1.80, 'BA\u00d1O 2\n4.7 m\u00b2', '#d4d8e8')
    d2y = WT + 3.00
    _rm(ax, rx, d2y, rw, 2.80, 'DORM 2\n7.3 m\u00b2', '#d4e8d4')
    _rm(ax, rx, WT, rw, 3.00, 'DORM 3\n7.8 m\u00b2', '#d4e8d4')
    _dh(ax, 0, 8.80, 7.6, '8.80 m', off=-0.5)
    _dv(ax, 0, 7.6, 12.00, '4.40 m', off=-0.5)
    _dh(ax, 8.80, 12.60, 0, '3.80 m', off=-0.5)
    _dv(ax, 12.60, 0, 12.00, '12.00 m', off=0.4)
    _dv(ax, 13.3, d1y, 12.00-WT, '3.30', off=0.3)
    _dv(ax, 13.3, b1y, d1y, '1.80', off=0.3)
    _dv(ax, 13.3, b2y, b1y, '1.80', off=0.3)
    _dv(ax, 13.3, d2y, d2y+2.80, '2.80', off=0.3)
    _dv(ax, 13.3, WT, WT+3.00, '3.00', off=0.3)
    _dh(ax, 8.80+WT, 8.80+WT+cw, -0.8, '0.90', off=0)
    for wx1, wx2 in [(1.5, 3.7), (4.2, 6.4)]:
        ax.plot([wx1, wx2], [7.6, 7.6], color='cyan', lw=5, alpha=0.5)
        ax.text((wx1+wx2)/2, 7.25, 'PV 2.20', fontsize=5, ha='center', color='teal')
    ax.plot([5.8, 8.1], [7.6, 7.6], color='cyan', lw=5, alpha=0.4)
    ax.text(6.95, 7.25, 'PUERTA 3.30', fontsize=5, ha='center', color='teal')
    ax.plot([8.80, 8.80], [8.0, 9.0], color='saddlebrown', lw=4, alpha=0.7)
    for wy, wh in [(9.5, 1.8), (3.8, 1.5), (0.8, 1.5)]:
        ax.plot([12.60, 12.60], [wy, wy+wh], color='cyan', lw=4, alpha=0.5)
    ax.text(4.4, 13.2, 'TOTAL: ~88 m\u00b2', fontsize=13,
            ha='center', fontweight='bold')
    ax.text(4.4, 12.6, 'Bloque A: 38.7 m\u00b2  +  Bloque B: 45.6 m\u00b2',
            fontsize=9, ha='center')
    ax.set_xlim(-1.5, 15.5); ax.set_ylim(-2, 14.5)
    ax.grid(True, alpha=0.15); ax.set_xlabel('m'); ax.set_ylabel('m')
    plt.tight_layout(); pdf.savefig(fig); plt.close()


def _page_guest_house(pdf):
    WT = 0.15
    fig, ax = plt.subplots(1, 1, figsize=(11.69, 8.27))
    ax.set_aspect('equal')
    ax.set_title('PLAN \u2014 GOSTEVOY DOM 33 m\u00b2 (3\u00d711)',
                 fontsize=14, fontweight='bold', pad=15)
    ax.add_patch(Rectangle((0, 0), 3.0, 11.0, fill=False,
                            edgecolor='black', lw=2.5))
    _rm(ax, WT, WT, 3.0-2*WT, 2.0-WT, 'SANUZAL\n6 m\u00b2', '#d4d8e8')
    _rm(ax, WT, 2.0, 3.0-2*WT, 4.0, 'SPALNYA\n12 m\u00b2', '#d4e8d4')
    _rm(ax, WT, 6.0, 3.0-2*WT, 5.0-WT,
        'GOSTINAYA\n+ KUHNYA\n15 m\u00b2', '#e8dcc8')
    _dh(ax, 0, 3.0, 0, '3.00 m', off=-0.5)
    _dv(ax, 3.0, 0, 11.0, '11.00 m', off=0.4)
    _dv(ax, -0.6, 0, 2.0, '2.00', off=0)
    _dv(ax, -0.6, 2.0, 6.0, '4.00', off=0)
    _dv(ax, -0.6, 6.0, 11.0, '5.00', off=0)
    ax.plot([3.0, 3.0], [8.0, 8.9], color='saddlebrown', lw=4, alpha=0.7)
    ax.text(3.4, 8.45, 'DVER', fontsize=6, color='saddlebrown')
    ax.plot([3.0, 3.0], [9.5, 10.85], color='cyan', lw=4, alpha=0.5)
    ax.text(3.4, 10.2, '1.80\u00d71.40', fontsize=5, color='teal')
    ax.plot([3.0, 3.0], [3.5, 4.7], color='cyan', lw=4, alpha=0.5)
    ax.text(3.4, 4.1, '1.20\u00d71.40', fontsize=5, color='teal')
    ax.plot([3.0, 3.0], [0.7, 1.3], color='cyan', lw=4, alpha=0.5)
    ax.text(3.4, 1.0, '0.60\u00d70.60', fontsize=5, color='teal')
    ax.plot([0.75, 2.25], [11.0, 11.0], color='cyan', lw=4, alpha=0.5)
    ax.text(1.5, 11.3, '1.50\u00d71.40', fontsize=5, color='teal', ha='center')
    ax.text(1.5, 12.0, 'KRYSHA: odnoskatnaya 4.0m \u2192 2.8m',
            fontsize=9, ha='center', fontstyle='italic')
    ax.text(1.5, -1.2, 'TOTAL: 33 m\u00b2', fontsize=13,
            ha='center', fontweight='bold')
    ax.set_xlim(-1.5, 6); ax.set_ylim(-2, 13)
    ax.grid(True, alpha=0.15); ax.set_xlabel('m'); ax.set_ylabel('m')
    plt.tight_layout(); pdf.savefig(fig); plt.close()


def _page_site_plan(pdf):
    fig, ax = plt.subplots(1, 1, figsize=(11.69, 8.27))
    ax.set_aspect('equal')
    ax.set_title('GENPLAN UCHASTKA 22\u00d755 m',
                 fontsize=14, fontweight='bold', pad=15)
    ax.add_patch(Rectangle((0, 0), 22, 50, fill=True, facecolor='#d4e8c4',
                            edgecolor='black', lw=2))
    ax.add_patch(Rectangle((0, 50), 22, 5, fill=True, facecolor='#8ba870',
                            edgecolor='black', lw=1.5))
    ax.text(11, 52.5, 'OVRAG (5 m, -3 m)', ha='center', fontsize=8,
            fontstyle='italic', color='#3a5a2a')
    ax.add_patch(Rectangle((0, 0), 22, 50, fill=False,
                            edgecolor='saddlebrown', lw=2, ls='--'))
    hx = (22 - 12.6) / 2
    hy = (50 - 12) / 2
    ax.add_patch(Rectangle((hx, hy+7.6), 8.80, 4.40, fill=True,
                            facecolor='#b0b0b4', edgecolor='black', lw=2))
    ax.add_patch(Rectangle((hx+8.80, hy), 3.80, 12.0, fill=True,
                            facecolor='#b0b0b4', edgecolor='black', lw=2))
    ax.text(hx+6, hy+9.8, 'DOM\n88 m\u00b2', ha='center',
            fontsize=10, fontweight='bold')
    gx, gy = 3.0, 4.0
    ax.add_patch(Rectangle((gx, gy), 3.0, 11.0, fill=True,
                            facecolor='#a0a0a4', edgecolor='black', lw=2))
    ax.text(gx+1.5, gy+5.5, 'GUEST\n33 m\u00b2', ha='center',
            fontsize=9, fontweight='bold')
    ax.add_patch(Rectangle((hx+0.5, hy+7.6-3.5), 7.8, 3.0, fill=True,
                            facecolor='#c8a878', edgecolor='black', lw=1, alpha=0.7))
    ax.text(hx+4.4, hy+6.1, 'TERRASA', ha='center',
            fontsize=6, fontstyle='italic')
    circle = plt.Circle((2.5, 47), 1.8, color='#2a8a2a', alpha=0.35)
    ax.add_patch(circle)
    ax.text(2.5, 47, 'Evkalipt', ha='center', fontsize=6, color='darkgreen')
    ax.add_patch(Rectangle((hx+8.80+0.2, 0), 1.5, hy, fill=True,
                            facecolor='#c0c0c0', edgecolor='gray', lw=0.5, alpha=0.5))
    _dh(ax, 0, 22, 0, '22.00 m', off=-2)
    _dv(ax, 22, 0, 55, '55.00 m', off=1.5)
    _dv(ax, 22, 50, 55, '5.00', off=1.5)
    _dh(ax, 0, gx, gy, '3 m', off=-0.8)
    _dv(ax, gx, 0, gy, '4 m', off=-0.6)
    _dv(ax, hx-0.5, 0, hy, '{:.1f} m'.format(hy), off=-0.3)
    ax.annotate('N', xy=(20.5, 48), fontsize=14, fontweight='bold', ha='center')
    ax.annotate('', xy=(20.5, 49.5), xytext=(20.5, 47),
                arrowprops=dict(arrowstyle='->', color='black', lw=2))
    ax.set_xlim(-3.5, 26); ax.set_ylim(-3.5, 58)
    ax.grid(True, alpha=0.12); ax.set_xlabel('m'); ax.set_ylabel('m')
    plt.tight_layout(); pdf.savefig(fig); plt.close()


def _generate(pdf_path):
    with PdfPages(pdf_path) as pdf:
        _page_main_house(pdf)
        _page_guest_house(pdf)
        _page_site_plan(pdf)


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..")
    build(out)
