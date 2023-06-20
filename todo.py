from flask import Flask,render_template,flash,redirect,url_for,session,logging,request
from flask_sqlalchemy import SQLAlchemy
from wtforms import Form,StringField,TextAreaField,PasswordField,validators,EmailField
from passlib.hash import sha256_crypt
from functools import wraps

#Kullanıcı giriş Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Bu sayfayı görüntülemek için giriş yapmalısınız...","danger")
            return redirect(url_for("login"))
    return decorated_function

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:////Users/user/Desktop/TodoApp/todo.db'
app.secret_key="secret_key"
db=SQLAlchemy(app)



@app.route("/")
def index():
    return render_template('index.html')

@app.route("/todo")
@login_required
def todo():
    results = Todo.query.filter_by(author=session["username"]).all()
    if results is not None:
        return render_template('todo.html',todolar = results)
    else:
        return render_template('todo.html')

@app.route("/login",methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST':
        username = form.username.data
        password_entered = form.password.data 

        search = register.query.filter_by(username=username).first()

        if search != None:
            data = register.query.filter_by(username=username).first()
            real_password = data.password
            if sha256_crypt.verify(password_entered,real_password):
                flash(category="success", message="Başarılıyla giriş yaptınız")                
                session["logged_in"]=True
                session["username"]=username
                return redirect(url_for("todo"))
            else:
                flash(category="danger",message="Kullanıcı Adı veya Parola Yanlış")
        else:
            flash(category="danger",message="Böyle bir kullanıcı yok...")
            return redirect(url_for("login"))
    return render_template('login.html',form=form)

@app.route("/kayıt", methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        username = form.username.data
        password = sha256_crypt.encrypt(form.password.data)
        newRegister = register(name=name, username=username, password=password)
        db.session.add(newRegister)
        db.session.commit()
        flash('Başarıyla Kayıt Oldun','success')
        return redirect(url_for("login"))
    else:
        return render_template('register.html',form=form)

@app.route("/complete/<string:id>")
def completeTodo(id):
    todo = Todo.query.filter_by(id = id).first()
    todo.complete = not todo.complete
    db.session.commit()
    return redirect(url_for("todo"))

@app.route("/add",methods=["POST"])
def addTodo():
    title = request.form.get('title')
    newTodo = Todo(title=title,complete=False,author = session["username"])
    db.session.add(newTodo)
    db.session.commit()
    return redirect(url_for("todo"))

@app.route("/delete/<string:id>")
def deleteTodo(id):
    todo = Todo.query.filter_by(id = id).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for("todo"))

@app.route("/logout")
def logout():
    session.clear()
    return  redirect(url_for("index"))

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80))
    complete = db.Column(db.Boolean)
    author = db.Column(db.Text)

class register(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    username = db.Column(db.Text)
    password = db.Column(db.Text)

class RegisterForm(Form):
    name = StringField("İsim Soyisim",validators=[validators.Length(min=4,max=25)])
    username = StringField("Kullanıcı Adı",validators=[validators.Length(min=5,max=35)])
    password = PasswordField("Parola",validators=[
        validators.DataRequired(message="Lütfen bir parola belirleyin"),
        validators.EqualTo(fieldname="confirm",message="Parolanız uyuşmuyor...")                        
    ])
    confirm = PasswordField("Parola Doğrula")

class LoginForm(Form):
    username = StringField("Kullanıcı Adı")
    password = PasswordField("Parola")






with app.app_context():
    db.create_all()


if __name__ == '__main__':
    
    app.run(debug=True)