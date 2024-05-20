from flask import Flask
from flask_cors import CORS
import getpass
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from datetime import datetime
import pandas as pd
import json
import requests
from flask import request, jsonify
from langchain import PromptTemplate
from langchain import hub
from langchain.docstore.document import Document
from langchain.document_loaders import WebBaseLoader
from langchain.schema import StrOutputParser
from langchain.schema.prompt_template import format_document
from langchain.schema.runnable import RunnablePassthrough
from langchain.vectorstores import Chroma
from langchain_core.messages import HumanMessage

from langchain_community.document_loaders import UnstructuredFileLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings


app = Flask(__name__)
CORS(app)

os.environ["GOOGLE_API_KEY"] = "ENTER_YOUR_API_KEY"

url_appliance = {
  "https://imgtr.ee/images/2024/05/02/41a3d1e31e7476604b0a7ddd9845853c.png" : "FRIDGE",
    "https://imgtr.ee/images/2024/05/02/e5800448e773c6a0ab4b96a22df3e5e4.png" : "FURNACE",
    "https://imgtr.ee/images/2024/05/02/c0f385e13fd45276070e6ce52944e7b6.png" : "KITCHEN",
    "https://imgtr.ee/images/2024/05/02/3d54f155ce9320fb63caf43448402724.png" : "BARN"
}

llm = ChatGoogleGenerativeAI(model="gemini-pro")
loader = UnstructuredFileLoader("output_temp_hum_press.txt")

docs = loader.load()

text_content = docs[0].page_content

text_content

docs =  [Document(page_content=text_content, metadata={"source": "local"})]

gemini_embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

vectorstore = Chroma.from_documents(
                     documents=docs,                 # Data
                     embedding=gemini_embeddings,    # Embedding model
                     persist_directory="./chroma_db" # Directory to save data
                     )

retriever = vectorstore.as_retriever(search_kwargs={"k": 1})

llm = ChatGoogleGenerativeAI(model="gemini-pro",
                 temperature=0.7, top_p=0.85)

from langchain_core.prompts import PromptTemplate
llm_text = ChatGoogleGenerativeAI(model="gemini-pro")
template = """
```
{context}

Each line of the data contains month name, day number of the month, mean temperature (in Fahrenheit), pressure, and humidity for the day.
```
{question}
Look at the graph, and provide 3-4 lines reasoning for the question, using weather data given in the context.
"""
prompt = PromptTemplate.from_template(template)
rag_chain = (
  {"context": retriever, "question": RunnablePassthrough()}
  | prompt
  | llm_text
  | StrOutputParser()
)

llm = ChatGoogleGenerativeAI(model="gemini-pro-vision")


#from IPython.display import Image
print("everything done")



@app.route('/', methods=['GET'])
def generate_report():
    date_str = request.args.get('date', default=None)
    hour = request.args.get('hour', type=int, default=-1)
    if not date_str:
        return jsonify({'error': 'Missing date parameter'}), 400

    try:
        # Load the datasets
        print("Current Working Directory:", os.getcwd())

        predicted_data = pd.read_csv('csv_files/predicted_combined.csv')
        actual_data = pd.read_csv('csv_files/test_combined.csv')

        # Convert the date string to a datetime object
        year, month, day = map(int, date_str.split('-'))
        if hour != -1:
            var = "hour"
        else:
            var = "day"

      # Filter data based on date
        date_filter = (predicted_data['month'] == month) & (predicted_data['day'] == day)

        if hour != -1:
            # Filter by specific hour
            filtered_predicted = predicted_data[date_filter & (predicted_data['hour'] == hour)]
            filtered_actual = actual_data[date_filter & (actual_data['hour'] == hour)]
        else:
            # Aggregate data for the entire day
            filtered_predicted = predicted_data[date_filter].groupby(['month', 'day']).sum().reset_index()
            filtered_actual = actual_data[date_filter].groupby(['month', 'day']).sum().reset_index()

        # Extract values to use in the prompt
        prompt_data = {
            "dishwasherPredicted": filtered_predicted['Dishwasher_predicted'].iloc[0],
            "dishwasherActual": filtered_actual['Dishwasher'].iloc[0],
            "homeOfficePredicted": filtered_predicted['Home office_predicted'].iloc[0],
            "homeOfficeActual": filtered_actual['Home office'].iloc[0],
            "fridgePredicted": filtered_predicted['Fridge_predicted'].iloc[0],
            "fridgeActual": filtered_actual['Fridge'].iloc[0],
            "wineCellarPredicted": filtered_predicted['Wine cellar_predicted'].iloc[0],
            "wineCellarActual": filtered_actual['Wine cellar'].iloc[0],
            "garageDoorPredicted": filtered_predicted['Garage door_predicted'].iloc[0],
            "garageDoorActual": filtered_actual['Garage door'].iloc[0],
            "barnPredicted": filtered_predicted['Barn_predicted'].iloc[0],
            "barnActual": filtered_actual['Barn'].iloc[0],
            "wellPredicted": filtered_predicted['Well_predicted'].iloc[0],
            "wellActual": filtered_actual['Well'].iloc[0],
            "microwavePredicted": filtered_predicted['Microwave_predicted'].iloc[0],
            "microwaveActual": filtered_actual['Microwave'].iloc[0],
            "livingRoomPredicted": filtered_predicted['Living room_predicted'].iloc[0],
            "livingRoomActual": filtered_actual['Living room'].iloc[0],
            "furnacePredicted": filtered_predicted['Furnace_predicted'].iloc[0],
            "furnaceActual": filtered_actual['Furnace'].iloc[0],
            "kitchenPredicted": filtered_predicted['Kitchen_predicted'].iloc[0],
            "kitchenActual": filtered_actual['Kitchen'].iloc[0],
        }

        llm = ChatGoogleGenerativeAI(model="gemini-pro")
        #Messages with System messages
        #1. Human message
        # Refigerator, Furnace, Microwave
        # Date, Month

        llm = ChatGoogleGenerativeAI(model="gemini-pro", convert_system_message_to_human=True)
        result = llm.invoke(
            [
                SystemMessage(content=f"you will be given expected and actual energy usage of some appliances for a particular {var}." \
                "Based on the above scenario, give an output to the user highlighting the economical advantage or disadvantage based on their actual use vs expected." \
                "Also highlight the ecological benefit/harm of the current actual use vs expected on environmental factors solely based on the impact user's usage will have.. Do not use numbers for ecological part. Quantify the economic savings."\
                "Also, only give user personalized recommendations and steps regarding how to use save energy for appliances which consumed more energy than expected. Commend them in recommendation section if they saved energy. The response should have these titles - Usage Summary, Economic Advantage/Disadvantage , Ecological Benefit/Harm, Recommendations and Steps. Add emojis wherever possible"),
                HumanMessage(content=f"expected Dishwasher Usage = {prompt_data['dishwasherPredicted']}, actual Dishwasher Usage = {prompt_data['dishwasherActual']}, expected Home office Usage = {prompt_data['homeOfficePredicted']}, actual Home office Usage = {prompt_data['homeOfficeActual']}, expected Fridge Usage = {prompt_data['fridgePredicted']}, actual Fridge Usage = {prompt_data['fridgeActual']}, expected Wine cellar Usage = {prompt_data['wineCellarPredicted']}, actual Wine cellar Usage = {prompt_data['wineCellarActual']}, expected Garage Door Usage = {prompt_data['garageDoorPredicted']}, actual Garage Door Usage = {prompt_data['garageDoorActual']}, expected Barn Usage = {prompt_data['barnPredicted']}, actual Barn Usage = {prompt_data['barnActual']}, expected Well Usage = {prompt_data['wellPredicted']}, actual Well Usage = {prompt_data['wellActual']}, expected Microwave Usage = {prompt_data['microwavePredicted']}, actual Microwave Usage = {prompt_data['microwaveActual']}, expected Living Room Usage = {prompt_data['livingRoomPredicted']}, actual Living Room Usage = {prompt_data['livingRoomActual']}, expected Furnace Usage = {prompt_data['furnacePredicted']}, actual Furnace Usage = {prompt_data['furnaceActual']}, expected Kitchen Usage = {prompt_data['kitchenPredicted']}, actual Kitchen Usage = {prompt_data['kitchenActual']}, Day = {day}, Month = {month}. Location = New York City. Per Watt usage = 23 cents. GIVE ATLEAST 2 STEPS TO SAVE ENERGY AT THE END OF THE REPORT, ONLY AFTER GIVING ALL COMPARISONS")
            ]
        )
        llm_response = result.content

        report_content = f"Report for {date_str} generated successfully."

        return jsonify({'report': report_content, 'llm_response': llm_response}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/langchain', methods=['POST'])
def langchain():
    data = request.get_json()
    image_url = data.get('image_url')
    user_question = data.get('user_question')


    llm_vision =  ChatGoogleGenerativeAI(model="gemini-pro-vision")
    full_chain = (
    RunnablePassthrough() | llm_vision | StrOutputParser() | rag_chain
    )

    message = HumanMessage(
    content=[
        {
        "type": "text",
        "text": f"This image is the time series plot of {url_appliance[image_url]} energy usage per month." \
        f"{user_question} in the image. The time series is not weather time series. Don't assume any actions about people, utilize the statistics in the context, and give the answer in terms of the appliance the question is meant for. THE APPLIANCE IS {url_appliance[image_url]}",
        }, # You can optionally provide text parts
        {"type": "image_url", "image_url": image_url},
    ])

    result = full_chain.invoke([message])
    return jsonify({'result': result})
if __name__ == '__main__':
    app.run(debug=True)
