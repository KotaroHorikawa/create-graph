from flask import Flask, render_template, request, jsonify
import numpy as np
import matplotlib
matplotlib.use('Agg')  # この行を追加
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

def evaluate_equation(equation, x_min, x_max):
    x = np.linspace(float(x_min), float(x_max), 1000)
    safe_dict = {
        'sin': np.sin, 'cos': np.cos, 'tan': np.tan,
        'exp': np.exp, 'log': np.log, 'sqrt': np.sqrt,
        'pi': np.pi, 'e': np.e, 'x': x,
        'abs': np.abs, 'real': np.real, 'imag': np.imag,
        'conj': np.conj, 'angle': np.angle, 'j': 1j
    }
    return eval(equation, {"__builtins__": None}, safe_dict)

def plot_equation(equation, x_min, x_max):
    plt.figure(figsize=(10, 8))
    plt.clf()  # この行を追加
    y = evaluate_equation(equation, x_min, x_max)
    
    if np.iscomplexobj(y) or isinstance(y, complex):
        if isinstance(y, (complex, np.complex128)):
            plt.plot([0, y.real], [0, y.imag], 'b-', linewidth=2)
            plt.plot([y.real], [y.imag], 'ro')
            plt.annotate(f'({y.real:.2f}, {y.imag:.2f}i)', 
                         xy=(y.real, y.imag), xytext=(5, 5),
                         textcoords='offset points')
        else:
            plt.plot(y.real, y.imag, 'b-')
        plt.title(f"複素数平面: {equation}")
        plt.xlabel("実部")
        plt.ylabel("虚部")
        plt.grid(True)
        plt.axhline(y=0, color='k', linestyle='--')
        plt.axvline(x=0, color='k', linestyle='--')
        max_abs = max(abs(np.max(y.real)), abs(np.max(y.imag)), abs(np.min(y.real)), abs(np.min(y.imag)))
        plt.xlim(-max_abs*1.1, max_abs*1.1)
        plt.ylim(-max_abs*1.1, max_abs*1.1)
        plt.gca().set_aspect('equal')
    else:
        x = np.linspace(float(x_min), float(x_max), 1000)
        if isinstance(y, (int, float, np.number)):
            plt.axhline(y=y, color='r')
        else:
            plt.plot(x, y)
        plt.title(f"y = {equation}")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.grid(True)
    
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()  # この行を追加
    return base64.b64encode(img.getvalue()).decode()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/plot', methods=['POST'])
def plot():
    data = request.json
    equation = data['equation']
    x_min = data['x_min']
    x_max = data['x_max']
    try:
        img_data = plot_equation(equation, x_min, x_max)
        return jsonify({'success': True, 'image': img_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)