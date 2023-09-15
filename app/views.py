import logging
import pydantic
import json
import glbvariables
import csv
from fastapi import APIRouter, HTTPException, Query, UploadFile, status
from sqlalchemy.exc import IntegrityError
from models import Business, Diagnosis, Symptoms
from contextlib import contextmanager
from database import SessionLocal
from io import StringIO

# setup loggers
logging.config.fileConfig('logging.conf', disable_existing_loggers=False)

# get root logger
logger = logging.getLogger(__name__) 
router = APIRouter()

# DB session creation and closing
@contextmanager
def create_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()  # Commit changes if successful
    except Exception as e:
        session.rollback()  # Rollback changes in case of an exception
        raise e
    finally:
        session.close()
        
# Class to help create a object of csv file data for each row 
class BusinessSymptom(pydantic.BaseModel):
    business_id: int | None = None
    business_name: str | None = "John Doe"
    symptom_id: str | None = None
    symptom_name: str | None ="John Doe"
    is_diagnosed: bool
    

@router.post("/upload_csv_file/")
async def create_file(csv_file: UploadFile):
    try:
        contents = await csv_file.read()
        decoded_contents = contents.decode('utf-8')
        csv_data = list(csv.DictReader(StringIO(decoded_contents)))
     
        logger.info("Adjusting ad filling empty data in missing cells")
        
        # Updating and filling data if empty
        for item in csv_data:
            
            item['Business ID'] = int(item['Business ID']) if item['Business ID'].strip() else glbvariables.DUMMY_BUSINESS_ID
            item['Business Name'] = item['Business Name'] or glbvariables.DUMMY_NAME
            item['Symptom Name'] = item['Symptom Name'] or glbvariables.DUMMY_NAME
            item['Symptom Code'] =item['Symptom Code'] or glbvariables.DUMMY_SYMPTOM_ID
            item['Symptom Diagnostic']=item['Symptom Diagnostic'].title() 
            
            if item['Symptom Diagnostic'] =='True' or item['Symptom Diagnostic']=='Yes':
                item['Symptom Diagnostic']= True
            else:
                item['Symptom Diagnostic'] = False
            
        
            mapped_item = {
                glbvariables.FILED_MAPPING[key]: value for key, value in item.items()
            }
            BusinessSymptom(**mapped_item) 

        logger.info("Changing key values of data based on mapping field dict")
        business_symptoms_csv = [
            BusinessSymptom(**{glbvariables.FILED_MAPPING[key]: value for key, value in item.items()})
            for item in csv_data
        ]
        logger.info("Function call to save CSV file data in database")

        # Function call to save data in the database
        save_data(business_symptoms_csv)

        return {"Message":"File processed succesfully" }

    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"KeyError: {str(e)}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"ValueError: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
        

def save_data(business_symptoms_csv):
    
    with create_session() as db:
        logger.info("Started saving data to DB")
        failed_item=[]
        
        try:
            for item in business_symptoms_csv:
                business_check = db.query(Business).filter_by(business_id=item.business_id).first()
                symptom_check = db.query(Symptoms).filter_by(symptom_id=item.symptom_id).first()
               
                if not business_check:
                    business_record=Business(
                        business_id=item.business_id,
                        business_name=item.business_name
                    )
                    db.add(business_record)
                elif(business_check.business_name != item.business_name):
                    business_check.business_name=item.business_name
                db.commit()
                    
                if not symptom_check:                
                    symptom_record=Symptoms(
                        symptom_id=item.symptom_id,
                        symptom_name=item.symptom_name
                    )
                    db.add(symptom_record)

                elif(symptom_check.symptom_name != item.symptom_name):
                    symptom_check.symptom_name=item.symptom_name
                
                db.commit()
            
            # Check is entry details have changed if yes update those 
            for item in business_symptoms_csv:
    
                diagnosis_check = db.query(Diagnosis)\
                    .filter(Diagnosis.business_id == item.business_id,\
                        Diagnosis.symptom_id == item.symptom_id\
                            ).first()
    
                if not diagnosis_check:
                    diagnosis_records=Diagnosis(
                        business_id=item.business_id,
                        symptom_id=item.symptom_id,
                        is_diagnosed=item.is_diagnosed
                    )
                    db.add(diagnosis_records )
                elif(diagnosis_check and (not diagnosis_check.is_diagnosed==item.is_diagnosed )):
                    diagnosis_check.is_diagnosed = item.is_diagnosed
                
                db.commit()
    
        except IntegrityError as e:
            db.rollback()  # Rollback the transaction for the item with duplicate primary key
            raise HTTPException(status_code=500, detail=f"Error inserting data into the database: {str(e)}")
    
    return {"message": "DB deleted succesfully"}
    
@router.get("/diagnostics_data/")
def get_data(BusinessID: int = Query(None, description="Filter by Business Name"),
    IsDiagnosed: bool= Query(None, description="Filter by Diognised")):
    
    try:
        with create_session() as db:
            
            # Joining tables with diagnosis table
            logger.info("Started executing quiery")
            query = db.query(
                Diagnosis.business_id,
                Business.business_name,
                Diagnosis.symptom_id,
                Symptoms.symptom_name,
                Diagnosis.is_diagnosed
            ).join(Diagnosis, Business.business_id == Diagnosis.business_id).join(
                Symptoms, Diagnosis.symptom_id == Symptoms.symptom_id
            )
            
            logger.info("Adding user input filters if anything is given")
            # Applying filters based on user input
            if BusinessID is not None:
                query = query.filter(Business.business_id == BusinessID)
            if IsDiagnosed is not None:
                query = query.filter(Diagnosis.is_diagnosed == IsDiagnosed)
        
            diagnosis_details = query.all()
            filtered_data=[]
            for item_data in diagnosis_details:
                business_id, business_name, symptom_id, symptom_name, is_diagnosed = item_data
                mappingdata_BS = BusinessSymptom(
                    business_id=business_id,
                    business_name=business_name,
                    symptom_id=symptom_id,
                    symptom_name=symptom_name,
                    is_diagnosed=is_diagnosed
                )
                filtered_data.append(mappingdata_BS)
            data = [dict(item) for item in filtered_data]
        
            return (data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred:"+str(e))

@router.post("/delete_data/")
def delete_data():
    with create_session() as db:
        try:
            # Clearing databse table content
            db.query(Business).delete()
            db.query(Symptoms).delete()
            db.query(Diagnosis).delete()
            db.commit()
        except Exception as e:
        
            db.rollback()
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"An error occurred while processing the file: {str(e)}")

    return {"message": "DB deleted succesfully"}