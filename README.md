# CMU Interactive Data Science Final Project

* **Online URL**: https://share.streamlit.io/cmu-ids-2022/final-project-mass-squad/sidharth
* **Team members**:
  * Contact person: anjadhav@andrew.cmu.edu
  * skathpal@andrew.cmu.edu
  * mvijay@andrew.cmu.edu
  * shreyas3@andrew.cmu.edu

## Work distribution

The contribution of each team member is listed below - 

* Aishwarya Jadhav - data preprocessing, map visualization
* Sidharth Kathpal - data preprocessing, overall rating distribution visualizations
* Shreya Sharma - data preprocessing, word cloud, rating distribution for individual restaurants
* Malaika Vijay - data preprocessing, similarity score computation, sentiment analysis, visualization comparing the ratings of businesses over time


## How to Run

### Environment Setup
To set up the environment, run <code> pip install -r requirements.txt </code>

### Data Preparation

* Download the reviews and business json data from this link - [Yelp Dataset](https://www.yelp.com/dataset/download)
* Preprocess the business json data by running <code> python business_preproc.py --in-file <path_to_business_json> --out-file <path_to_output_csv> </code>
* Preprocess the reviews json data by running <code> python reviews_preproc.py --in-file <path_to_reviews_json> --out-file <path_to_output_csv> --business-file <path_to_preprocessed_business_csv> </code>

### Run the Streamlit Application 

 To run the streamlit application, run <code> streamlit run streamlit_app.py </code>

## Deliverables

### Proposal

- [ ] The URL at the top of this readme needs to point to your application online. It should also list the names of the team members.
- [ ] A completed [proposal](Proposal.md). Each student should submit the URL that points to this file in their github repo on Canvas.

### Sketches

- [ ] Develop sketches/prototype of your project.

### Final deliverables

- [ ] All code for the project should be in the repo.
- [ ] Update the **Online URL** above to point to your deployed project.
- [ ] A detailed [project report](Report.md).  Each student should submit the URL that points to this file in their github repo on Canvas.
- [ ] A 5 minute video demonstration.  Upload the video to this github repo and link to it from your report.
