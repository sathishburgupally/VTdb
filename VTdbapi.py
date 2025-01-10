from flask import Flask, request, jsonify, Response
from mysql.connector import connect
from sqlalchemy import create_engine
from flask_cors import CORS
import pandas as pd
import json
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain
import os
import uuid
import warnings
warnings.simplefilter("ignore")

app =  Flask(__name__)
CORS(app)
llm  =  ChatOpenAI(api_key = os.getenv('OPENAI_API_KEY'),model ="gpt-3.5-turbo", temperature  =0.1)
@app.route("/signup",methods =["POST"])
def signin():
    data =  request.get_json()
    email =  data.get('email')
    username =  data.get('username')
    password = data.get('password')
    ph =  data.get('phone')
    if not email or not username or not ph or not password:
        return jsonify({\
            'response' : "Please enter all the values"

        })
    else :
       res = check1(email=email)
       if res:
           return  jsonify({
               'response' : 'user already existed'
           })
       try :
        connecter =  connect(host ="seo-bot.cvpmgfsxtfk7.ap-south-1.rds.amazonaws.com", user='admin',password ='N1ArkkLPHN28',db = 'virginia_tiles')
        cursor  =  connecter.cursor()
        cmd = '''
            INSERT INTO user_creds (email, username, phone,password) VALUES (%s, %s, %s, %s)
                '''
        cursor.execute(cmd,(email,username,ph,password))
        connecter.commit()
        connecter.close()
        return jsonify({
            'response' : 'user sucessfully created'
        })
       except  Exception as e:
           return jsonify(
               {
                   'response' : 'Unable to connect database'+str(e)
               }
           )
        

@app.route('/check',methods  = ["POST",'GET'])
def check():
    data  =  request.get_json()
    email  =  data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({
            'response' : 'No Email or Password found'
        }) 
    else :
        try :
            connecter =  connect(host ="seo-bot.cvpmgfsxtfk7.ap-south-1.rds.amazonaws.com", user='admin',password ='N1ArkkLPHN28',db = 'virginia_tiles')
            cursor  =  connecter.cursor()
            cmd = '''
            SELECT * FROM user_creds WHERE email = %s
                '''
            cursor.execute(cmd,[email])

            l1 = cursor.fetchone()
            connecter.close()
          
        except Exception as e:
            return jsonify({
                'response' : 'Unable to connect database' +str(e)
            })
        if l1:
            # l1 = cursor.fetchone()

            if l1[-1] ==password:
                # print(password)
                username =  l1[1]
                # print(username)
                
                return jsonify({
                    'email':email,
                    'username' :username
                })
            else :
                return jsonify(
                    {
                        'response' : 'Incorrect password'
                    }
                )
        
        else : 
            return jsonify(
                {'response' : 'No account found'}
            )

def check1(email=None):
    if not email:
        return "No email found"
    else :
        try :
            connecter =  connect(host ="seo-bot.cvpmgfsxtfk7.ap-south-1.rds.amazonaws.com", user='admin',password ='N1ArkkLPHN28',db = 'virginia_tiles')
            cursor  =  connecter.cursor()
            cmd = '''
            SELECT * FROM user_creds WHERE email = %s
                    '''
            cursor.execute(cmd,[email])

            l1 = cursor.fetchone()
        except :
            return False
        connecter.close()
        if l1:
            if email in l1:
                return True
            else :
                return False
        else : 
            return False
            


@app.route('/comment_section',methods = ["post"])
def comment_section():
    data =  request.get_json()
    email =  data.get('email')
    post_type = data.get('post_type')
    question_no = data.get('question_no')
    post_name = data.get('post_name')
    user_comment = data.get('user_comment')
    statement_type = data.get('statement_type')
    if not user_comment or not email or not post_name or not post_type or not question_no:
        return jsonify({
            'response' : 'Please provide all the details'
        })
    res =  check1(email=email)
    if res:
        try :
            connecter =  connect(host ="seo-bot.cvpmgfsxtfk7.ap-south-1.rds.amazonaws.com", user='admin',password ='N1ArkkLPHN28',db = 'virginia_tiles')
            cursor  =  connecter.cursor()
            cmd = '''
                INSERT INTO comment_section (email, post_type, question_no, post_name, user_comment, statement_type) VALUES (%s, %s, %s, %s, %s, %s)
                    '''
            cursor.execute(cmd,(email, post_type, question_no,post_name,user_comment,statement_type   ))
            connecter.commit()
            connecter.close()
        except Exception as e:
            return  jsonify({
                'response' : 'Unable to connect database'+str(e)
            })

        return jsonify({'response':'sucessfully your comment noted'})
    else :
        return jsonify({
            'response' : 'no account found'
        })


@app.route('/fetch', methods = ["POST"])
def fetch():
    data  =  request.get_json()
    email =  data.get("email")
    post_type = data.get('post_type')
    question_no = data.get('question_no')
    post_name = data.get('post_name')
    statement_type = data.get('statement_type')
    if not all([email,post_name,question_no,question_no,statement_type]):
        return jsonify({
            'response' : "please enter all the values"
        })
    else :
        try :
            db  = connect(host ="seo-bot.cvpmgfsxtfk7.ap-south-1.rds.amazonaws.com",user='admin',password ='N1ArkkLPHN28',db ="virginia_tiles")
            df =  pd.read_sql('SELECT * FROM user_creds',db)
            df1 = pd.read_sql('SELECT * FROM comment_section',db)
            db.close()
        except Exception as e :
            return jsonify({
                'response' : 'AN error occured' + str(e)
            })
        v = df1["email"][(df1["question_no"]==question_no)&(df1["statement_type"]==statement_type)&(df1["post_type"]==post_type)&(df1["post_name"]==post_name)].values.tolist()
        if v:
            username  =df["username"][df["email"]==v[0]].values[0]
            comments  = df1["user_comment"][(df1["question_no"]==question_no)&(df1["statement_type"]==statement_type)&(df1["post_type"]==post_type)&(df1["post_name"]==post_name)].values.tolist()
            intervels  = df1["create_at"][(df1["question_no"]==6)&(df1["statement_type"]=="Q")&(df1["post_type"]=="PL")&(df1["post_name"]=="Agate")].values.tolist()
            return jsonify({
                'comments' :comments ,
                'intervels' : intervels
            },540)
        else :
            return Response(status  = 420)

@app.route("/faqs",methods =["GET"])
def faqs():
    line  =  request.args.get('line')
    if not line :
        return Response(status=520)
    else :
        connecter =  connect(host ="seo-bot.cvpmgfsxtfk7.ap-south-1.rds.amazonaws.com", user='admin',password ='N1ArkkLPHN28',db = 'virginia_tiles') 
        df_pl  = pd.read_sql("select * from product_lines",connecter) 
        connecter.close()

        if line in df_pl["product_line"].to_list():
            FAQS = json.loads(df_pl["faqs"][df_pl["product_line"]==line].values[0])
            description = df_pl["description"][df_pl["product_line"]==line].values[0]
            return jsonify({
                'response' :FAQS,
                'description': description
            })
            
        else :
            return jsonify({
                'response' :"Sorry No product line found"
            }) 



@app.route('/humanize', methods=["POST"])
def humanize():
    data = request.get_json()
    text = data.get('faqs')
    des = data.get('des')
    email = data.get('email')
    post_type = data.get('post_type')
    question_no = data.get('question_no')
    post_name = data.get('post_name')
    user_comment = data.get('user_comment')
    statement_type = data.get('statement_type')

    if not text or not des:
        return jsonify({'response': 'Please provide both FAQs and description'})
    res  =  check1(email=email)
    if res :
        # Construct the text for the FAQ and description
        text = '\nFAQs:\n' + text + '\n\nDescription:\n' + des

        prompt = '''
        As a human assistant named Swaroop, your main task is to thoroughly review and rephrase the provided sentences. Make essential adjustments to ensure they are written in a way that bypasses detection by ZEROGPT or any similar tools designed to identify machine-generated content. When rewriting FAQs, focus on maintaining low perplexity and high burstiness to improve readability and engagement.
        You have two types of texts: one is FAQ's and another is the description, so rewrite them accordingly.

        faqs should folow the fowwouwing structure
        {{'faqs':[{{'Q1':'A1','Q2':'A2'}}],'Description':'refined_description'}}

        **Things to Remember**
        Give me the data in JSON format of FAQ's & description and no need of any other headings or side headings. json keys must be FAQS and Description.
        '''
        try:

            connecter =  connect(host ="seo-bot.cvpmgfsxtfk7.ap-south-1.rds.amazonaws.com", user='admin',password ='N1ArkkLPHN28',db = 'virginia_tiles')
            cursor  =  connecter.cursor()

            # Define the prompt template
            prompt_template = ChatPromptTemplate.from_messages([
                ("system", prompt),
                ("user", "{text}")
            ])
            prompt_template.input_variables = ['text']
            # Create a chain with the model and the prompt
            chain = prompt_template|llm

            # Run the chain with the provided text
            
            response = json.loads(chain.invoke({"text": text}).content)
            print(response.keys())
            faqs = response.get("FAQs")
            description =  response.get("Description")
            print(faqs,'\n\n\n\n\n',description)
            cmd = '''
                INSERT INTO comment_section (email, post_type, question_no, post_name, user_comment, statement_type,faqs, description, unique_key) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)
                    '''
            cursor.execute(cmd,(email, post_type, question_no, post_name, user_comment, statement_type, str(faqs), description, str(uuid.uuid1())))
            connecter.commit()
            connecter.close()
            print("suxessfully humanised")
            # Return the humanized response
            return jsonify({'response': response})

        except Exception as e:
            print(f"Error: {e}")
            connecter.close()
            return jsonify({'response': f'An error occurred: {e}. Please try again later.'}), 500
            
    else :
        return Response(status=500)


@app.route('/regenerate',methods  = ["POST"])
def regenerate():
    data = request.get_json()
    text = data.get('data')
    des = data.get('des')
    email = data.get('email')
    post_type = data.get('post_type')
    question_no = data.get('question_no')
    post_name = data.get('post_name')
    user_comment = data.get('user_comment')
    statement_type = data.get('statement_type')
    product_line  =  data.get('product_line')

    if not all(email, post_type, question_no, post_name, user_comment, statement_type, des,text):
        connecter =  connect(host ="seo-bot.cvpmgfsxtfk7.ap-south-1.rds.amazonaws.com", user='admin',password ='N1ArkkLPHN28',db = 'virginia_tiles')
        cursor  =  connecter.cursor()
        df = pd.read_sql("select * from product_lines",connecter)
        template = '''
        As a human assistant named Swaroop, your task is to rewrite the provided FAQ based on the user's comment and the product line data. You must maintain the integrity of the FAQ information while improving readability and user engagement. Ensure the FAQ is rewritten concisely and clearly, while considering the user's feedback.

        The output must be provided in JSON format only.

        FAQS : {faqs},
        question no : {question_no}
        product line data : {data}
        '''
        prompt =  ChatPromptTemplate.from_template(
            template=template
        )
        data  =  df["product_line_data"][df["product_line"]==product_line].values.tolist()[0]
        if not data:
            return jsonify({'response':'No product line found'})
        else  :
            chain  =  prompt|llm
            response =  chain.invoke({
                'faqs' :faqs,
                'question_no' : question_no,
                'data' :data
            }).content
            faqs  = json.loads(response)
            cmd = '''
                INSERT INTO comment_section (email, post_type, question_no, post_name, user_comment, statement_type,faqs, descrption, unique_id) VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)
                    '''
            cursor.execute(cmd,(email, post_type, question_no, post_name, user_comment, statement_type, faqs, des, str(uuid.uuid1())))
            connecter.commit()
            connecter.close()
    else :
        return {
            'response' : 'please enter all the values'
        }



@app.errorhandler(404)
def errorhander(e):
    return jsonify(
        {
            "response" : "no API found"
        }
    )





@app.errorhandler(405)
def errorhander(e):
    return jsonify(
        {
            "response" : "This method canot be allowed"
        }
    )


if __name__ =='__main__' :
    app.run(host="0.0.0.0",port=4285, debug=True)

        



