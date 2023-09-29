from datetime import datetime, timedelta

deadline_choices = ["2-3 Weeks","1 Month","2 Months", "3 Months","4 Months"]
job_type = ["Frontend Engineer","Backend Engineer","Full Stack Engineer","Product Design","Data Analysis"]
job_experiences = ["less than a year","1-2 years","2-3 years" ,"3-4 years","4-5 years"]
jobposts_pays = ["150,000-250,000","250,000-350,000","350,000-450,000","450,000-550,000","650,000-750,000"]

deadline_mapping = {
            "2-3 Weeks": timedelta(weeks=2),
            "1 Month": timedelta(weeks=4),
            "2 Months": timedelta(weeks=8),
            "3 Months": timedelta(weeks=12),
            "4 Months": timedelta(weeks=16),
        }