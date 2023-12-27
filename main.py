from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from webforms import AddUserform, LoginForm, UpdateUser, Chatform
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

from typing import Any
from langchain.memory.chat_message_histories import SQLChatMessageHistory
from langchain.memory.chat_message_histories.sql import BaseMessageConverter
from langchain.schema import AIMessage, BaseMessage, HumanMessage, SystemMessage
from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


#create a flask instance
app = Flask(__name__)
#add database/old db
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

#mysqldb
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:bystander_669@localhost/users"

#secret key
app.config['SECRET_KEY'] = "password"

#for flask login
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))
    
#initialize db
db = SQLAlchemy(app)
migrate = Migrate(app, db)
#create model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def password(self):
        raise AttributeError('password not readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    #create string
    def __repr__(self):
        return '<Name %r>' % self.name
with app.app_context():
    db.create_all()


Base = declarative_base()


class CustomMessage(Base):
    __tablename__ = "custom_message_store"

    id = Column(Integer, primary_key=True)
    session_id = Column(Text)
    type = Column(Text)
    content = Column(Text)
    created_at = Column(DateTime)
    author_email = Column(Text)


class CustomMessageConverter(BaseMessageConverter):
    def __init__(self, author_email: str):
        self.author_email = author_email

    def from_sql_model(self, sql_message: Any) -> BaseMessage:
        if sql_message.type == "human":
            return HumanMessage(
                content=sql_message.content,
            )
        elif sql_message.type == "ai":
            return AIMessage(
                content=sql_message.content,
            )
        elif sql_message.type == "system":
            return SystemMessage(
                content=sql_message.content,
            )
        else:
            raise ValueError(f"Unknown message type: {sql_message.type}")

    def to_sql_model(self, message: BaseMessage, session_id: str) -> Any:
        now = datetime.now()
        return CustomMessage(
            session_id=session_id,
            type=message.type,
            content=message.content,
            created_at=now,
            author_email=self.author_email,
        )

    def get_sql_model_class(self) -> Any:
        return CustomMessage




#create a route decorator
@app.route('/')
def index():
    sentence = 'teach <strong>me</strong> something'
    fruits = ['apple','banana','durian','mango',69]
    return render_template('index.html',sentence=sentence,fruits=fruits)


#http://127.0.0.1:5000/user/(custom name)
@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


#error handler for error 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'),404


#error handler for error 500
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'),500





@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("login successfully")
                return redirect(url_for('dashboard'))
            else:
                flash('wrong password')
        else:
            flash('user doesnt exist')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("logout successfully")
    return redirect(url_for('login'))


#update record in database
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UpdateUser()
    name_to_update = Users.query.get_or_404(id)
    our_users = Users.query.order_by(Users.date_added)
    if form.validate_on_submit():
        name_to_update.username = form.username.data
        name_to_update.name = form.name.data
        name_to_update.email = form.email.data
        try:
            db.session.commit()
            flash("User Updated Succ")
            return redirect(url_for('dashboard'))
        except:
            flash("Update failed....try again")
            return render_template('update.html', form=form, name_to_update=name_to_update, id=id, our_users=our_users)
    else:
        return render_template('update.html', form=form, name_to_update=name_to_update, our_users=our_users, id=id)

#create route to AddUser
@app.route('/user/add', methods=['GET','POST'])
def add_user():
    name = None
    form = AddUserform()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user2 = Users.query.filter_by(username=form.username.data).first()
            if user2 is None:
                pass_hash = generate_password_hash(form.password_hash.data, method='scrypt')
                user = Users(username = form.username.data, name=form.name.data, email=form.email.data, password_hash = pass_hash)
                db.session.add(user)
                db.session.commit()
                name = form.name.data
                form.username.data = ''
                form.name.data = ''
                form.email.data = ''
                form.password_hash.data = ''
                flash("User Added Successfully")
            else:
                flash("username already exists")
        else:
            flash("email already exists")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, our_users=our_users)

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("user deleted")
        return redirect(url_for('add_user'))
    except:
        flash('something went wrong')
        name = None
        form = AddUserform()
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, our_users=our_users)
    


from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import WebBaseLoader
from langchain.vectorstores.chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.chains import RetrievalQA
from langchain.memory import ConversationBufferWindowMemory
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts.prompt import PromptTemplate
from langchain.llms import OpenAI
from langchain.embeddings import HuggingFaceEmbeddings



@app.route('/chatbot', methods=['GET','POST'])
@login_required
def chatbot():
    message_history = SQLChatMessageHistory(
    session_id="test_session",
    connection_string="mysql+mysqlconnector://root:bystander_669@localhost/users",
    custom_message_converter=CustomMessageConverter(author_email=current_user.email),
    )
    messages = message_history.messages
    current_user_email = current_user.email
    form = Chatform()
    if form.validate_on_submit():
        question = form.question.data
        response = run_openai_llm_chain(question, message_history)
        formatted_response = response.replace('\n', '<br>')
        form.question.data = ''
        return render_template('chatbot.html', question=question, formatted_response=formatted_response, form=form, messages=messages, current_user_email=current_user_email)
    else:
        form = Chatform()
    form.question.data = ''
    return render_template('chatbot.html', form=form, messages=messages, current_user_email=current_user_email)

 
def load_vectorstore():
    persist_directory = 'vectore_db'
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    if os.path.exists(persist_directory):
        # If it exists, load the existing vector store
        vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    else:
        loader = WebBaseLoader('https://msugensan.edu.ph/admissions/')
        web_text = loader.load()
        text_splitter = CharacterTextSplitter(length_function=len, chunk_size=2000, chunk_overlap=100)
        documents = text_splitter.split_documents(web_text)
        vectordb = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory = persist_directory)
        vectordb.persist()
    return vectordb

def run_openai_llm_chain(question, message_history):
    vectordb = load_vectorstore()
    
    template = """
    Use the following context (delimited by <ctx></ctx>) and the chat history (delimited by <hs></hs>) to answer the question:
    ------
    <ctx>
    {context}
    </ctx>
    ------
    <hs>
    {chat_history}
    </hs>
    ------
    {question}
    Answer:
    """
    prompt = PromptTemplate(
    input_variables=["chat_history", "context", "question"],
    template=template,
    )

    # chat completion llm
    llm = ChatOpenAI(openai_api_key="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", temperature=0.3)


    
    qa = RetrievalQA.from_chain_type(
    llm=llm, 
    chain_type='stuff',
    retriever=vectordb.as_retriever(),
    chain_type_kwargs={
        "verbose": True,
        "prompt": prompt,
        "memory": ConversationBufferWindowMemory(
            chat_memory=message_history,
            memory_key='chat_history',
            input_key='question',
            k=4
            )
        }
    )
   
    respond = qa.run(question)
    return respond


from langchain.utilities import SQLDatabase
from langchain_experimental.sql import SQLDatabaseChain

@app.route('/adminbot', methods=['GET','POST'])
@login_required
def adminbot():
    db = SQLDatabase.from_uri("mysql+mysqlconnector://root:bystander_669@localhost/users")
    llm = OpenAI(temperature=0, verbose=True, openai_api_key="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")
    form = Chatform()
    if form.validate_on_submit():
        question = form.question.data
        db_chain = SQLDatabaseChain.from_llm(llm, db, verbose=True)
        answer = db_chain.run(question)
        formatted_answer = answer.replace('\n', '<br>')
        form.question.data = ''
        return render_template('adminbot.html', question=question, formatted_answer=formatted_answer, form=form)
    else:
        form = Chatform()
    form.question.data = ''
    return render_template('adminbot.html', form=form)