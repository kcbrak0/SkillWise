import streamlit as st
import pandas as pd
import base64,random
import time,datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import pafy
import plotly.express as px
import nltk
nltk.download('stopwords')
nltk.data.path.append('\Lib\stopwords')

def fetch_yt_video(link):
    video = pafy.new(link)
    return video.title

def get_table_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # Bazi degerlerin byte donusumu gerekiyor ve burada gerceklesiyor.
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    # pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def course_recommender(course_list):
    st.subheader("SkillWise")
    c = 0
    rec_course = []
    no_of_reco = st.slider('Tavsiye Kurslarimiz', 1, 5, 3)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course

connection = pymysql.connect(host='localhost',user='root',password='',db='rc')
cursor = connection.cursor()

def insert_data(name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (name, email, str(res_score), timestamp,str(no_of_pages), reco_field, cand_level, skills,recommended_skills,courses)
    cursor.execute(insert_sql, rec_values)
    connection.commit()

st.set_page_config(
   page_title="SkillWise",
   page_icon='C:/Users/burak/Desktop/ResumeCollection/Logo/RC_Logo.png',
)
def run():
    st.title("SkillWise")
    st.sidebar.markdown("Kullanici Tipi")
    activities = ["Kullanici", "Admin"]
    choice = st.sidebar.selectbox("Kullanici Tipinizi Seciniz", activities)
    img = Image.open("C:/Users/burak/Desktop/ResumeCollection/Logo/RC_Logo.png")
    img = img.resize((250,250))
    st.image(img)

    
    db_sql = """CREATE DATABASE IF NOT EXISTS RC;"""
    cursor.execute(db_sql)

   
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(100) NOT NULL,
                     Email_ID VARCHAR(50) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field VARCHAR(25) NOT NULL,
                     User_level VARCHAR(30) NOT NULL,
                     Actual_skills VARCHAR(300) NOT NULL,
                     Recommended_skills VARCHAR(300) NOT NULL,
                     Recommended_courses VARCHAR(600) NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    if choice == 'Kullanici':
        pdf_file = st.file_uploader("Yuklemek Istediginiz CV Seciniz", type=["pdf"])
        if pdf_file is not None:
            save_image_path = "C:/Users/burak/Desktop/ResumeCollection/Uploaded_Resumes/"+pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                
                resume_text = pdf_reader(save_image_path)

                st.header("*CV Analiziniz*")
                st.success("Merhaba "+ resume_data['name'])
                st.subheader("*Bilgileriniz*")
                try:
                    st.text('Isim: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Iletisim: ' + resume_data['mobile_number'])
                    st.text('Sayfa Sayisi: '+str(resume_data['no_of_pages']))
                except:
                    pass
                cand_level = ''
                if resume_data['no_of_pages'] == 1:
                    cand_level = "Junior"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>Cv'nize Gore Junior olarak gozukuyorsunuz</h4>''',unsafe_allow_html=True)
                elif resume_data['no_of_pages'] == 2:
                    cand_level = "Mid-Level"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Cv'nize Gore Mid-Level olarak gozukuyorsunuz</h4>''',unsafe_allow_html=True)
                elif resume_data['no_of_pages'] >=3:
                    cand_level = "Senior"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'Cv'nize Gore Senior olarak gozukuyorsunuz''',unsafe_allow_html=True)

                st.subheader("*Tavsiyelerimiz*")
                
                keywords = st_tags(label='### Sahip Oldugun Yetenekler',
                text='Bu Yeteneklerde Kendini Gelistirebilirsin',
                    value=resume_data['skills'],key = '1')

                
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'c#', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']

                recommended_skills = []
                reco_field = ''
                rec_course = ''
                ## Kurs Tavsiyeleri
                for i in resume_data['skills']:
                    ## Veri Bilimci
                    if i.lower() in ds_keyword:
                        print(i.lower())
                        reco_field = 'Data Science'
                        st.success("*Analizlerimize Gore Veri Bilimci Is Ilanlarina Bakiyorsunuz*")
                        recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                        recommended_keywords = st_tags(label='#Sahip Olman Gereken Yetenekler',
                        text='Sistem Tarafindan Onerilen Yetenkler',value=recommended_skills,key = '2')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Bu yetenekleri edinmeniz istediginiz alanda is bulmanizi kolaylastiracaktir.</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(ds_course)
                        break

                    ## Web Developer
                    elif i.lower() in web_keyword:
                        print(i.lower())
                        reco_field = 'Web Development'
                        st.success("* Analizlerimize Gore Web Development Is Ilanlarina Bakiyorsunuz *")
                        recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                        recommended_keywords = st_tags(label='#Sahip Olman Gereken Yetenekler',
                        text='Sistem Tarafindan Onerilen Yetenkler',value=recommended_skills,key = '3')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Bu yetenekleri edinmeniz istediginiz alanda is bulmanizi kolaylastiracaktir.</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(web_course)
                        break

                    ## Android Developer
                    elif i.lower() in android_keyword:
                        print(i.lower())
                        reco_field = 'Android Development'
                        st.success("*Analizlerimize Gore Android Development Is Ilanlarina Bakiyorsunuz*")
                        recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                        recommended_keywords = st_tags(label='#Sahip Olman Gereken Yetenekler',
                        text='Sistem Tarafindan Onerilen Yetenkler',value=recommended_skills,key = '4')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Bu yetenekleri edinmeniz istediginiz alanda is bulmanizi kolaylastiracaktir.</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(android_course)
                        break

                    ## IOS Developer
                    elif i.lower() in ios_keyword:
                        print(i.lower())
                        reco_field = 'IOS Development'
                        st.success("*Analizlerimize Gore IOS Development Is Ilanlarina Bakiyorsunuz*")
                        recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                        recommended_keywords = st_tags(label='#Sahip Olman Gereken Yetenekler',
                        text='Sistem Tarafindan Onerilen Yetenkler',value=recommended_skills,key = '5')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Bu yetenekleri edinmeniz istediginiz alanda is bulmanizi kolaylastiracaktir.</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(ios_course)
                        break

                    ## Ui-UX
                    elif i.lower() in uiux_keyword:
                        print(i.lower())
                        reco_field = 'UI-UX Development'
                        st.success("**Analizlerimize Gore UI-UX Is Ilanlarina Bakiyorsunuz**")
                        recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                        recommended_keywords = st_tags(label='#Sahip Olman Gereken Yetenekler',
                        text='Sistem Tarafindan Onerilen Yetenkler',value=recommended_skills,key = '6')
                        st.markdown('''<h4 style='text-align: left; color: #1ed760;'>Bu yetenekleri edinmeniz istediginiz alanda is bulmanizi kolaylastiracaktir.</h4>''',unsafe_allow_html=True)
                        rec_course = course_recommender(uiux_course)
                        break

                #
                #DB eklemek icin zaman
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)

                #CV Puanlama ve Degerlendirme Kriterleri
                st.subheader("*CV'niz Icin Onerilerimiz*")
                resume_score = 0
                if 'HAKKINDA' in resume_text:
                    resume_score = resume_score+20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Harika! Hakkinda bilgi vermissin</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] Hakkinda daha detayli bilgi vermen seni tanimalarina yardimci olacaktir.</h4>''',unsafe_allow_html=True)

                if 'Dil Bilgisi'  in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Harika! Bildigin diller ile ilgili bilgi vermissin/h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] Bildigin diller hakkinda daha detayli bilgi vermen seni is icin uygunlugunu gosterecektir.</h4>''',unsafe_allow_html=True)

                if 'Hobiler' or 'Eglence'in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Harika! Hobilerin bilgi vermissin</h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] Hobilerin hakkinda bilgi vermen seni daha iyi tanimalarina olanak saglar</h4>''',unsafe_allow_html=True)

                if 'SERTİFİKALAR' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Harika! Sertifikalarin bilgi vermissin </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] Sertifikalarin daha detayli bilgi vermen seni is icin uygunlugunu gosterecektir.</h4>''',unsafe_allow_html=True)

                if 'Projeler' in resume_text:
                    resume_score = resume_score + 20
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>[+] Harika! Projelerin bilgi vermissin </h4>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<h4 style='text-align: left; color: #fabc10;'>[-] Projelerin daha detayli bilgi vermen seni is icin uygunlugunu gosterecektir.</h4>''',unsafe_allow_html=True)

                st.subheader("**CV Puani**")
                st.markdown(
                    """
                    <style>
                        .stProgress > div > div > div > div {
                            background-color: #d73b5c;
                        }
                    </style>""",
                    unsafe_allow_html=True,
                )
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)
                st.success('** CV Puaniniz:  ' + str(score)+'**')
                st.warning("** Not: Bu puan, Ozgecmisinize eklediginiz icerige gore hesaplanir. **")
                st.balloons()

                insert_data(resume_data['name'], resume_data['email'], str(resume_score), timestamp,
                              str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']),
                              str(recommended_skills), str(rec_course))


               

                connection.commit()
            else:
                st.error('Birseyler yanlis gitti.')
    else:
        
        st.success('Admin Paneline Hos Geldiniz')
        
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')
        if st.button('Login'):
            if ad_user == 'deneme' and ad_password == 'deneme':
                st.success("Hosgeldiniz")
                
                cursor.execute('''SELECT*FROM user_data''')
                data = cursor.fetchall()
                st.header("**Kullanici Kayitlari**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                                                 'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                                                 'Recommended Course'])
                st.dataframe(df)
                st.markdown(get_table_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)
                
                query = 'select * from user_data;'
                plot_data = pd.read_sql(query, connection)

                
                labels = plot_data.Predicted_Field.unique()
                print(labels)
                values = plot_data.Predicted_Field.value_counts()
                print(values)
                st.subheader(" **Oneriler Icin Olusturulan Grafik**")
                fig = px.pie(df, values=values, names=labels, title='Becerilere Gore Tercih Edilmesi Gereken Alanlar')
                st.plotly_chart(fig)

               
                labels = plot_data.User_level.unique()
                values = plot_data.User_level.value_counts()
                st.subheader("** Kullanicilarin Seviyeleri Icın Olusturulan Grafik**")
                fig = px.pie(df, values=values, names=labels, title="Kullanicilerin Deneyim Seviyeleri")
                st.plotly_chart(fig)


            else:
                st.error("Yanlis kullanici adi ve parola")
run()