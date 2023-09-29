from django.db import models

class JobPoster(models.Model):
    id = models.AutoField(primary_key=True)
    full_name = models.CharField(max_length=250)
    email = models.EmailField()
    
    def __str__(self):
        return self.full_name
    

class JobPost(models.Model):
    jobposters = models.ForeignKey('JobPoster',related_name="job_poster_jobs",on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    location = models.CharField(max_length=250)
    
    JOB_POST_TYPES = [
        ("Web Development", "Web Development"),
        ("Product Design", "Product Design"),
        ("Data Analysis", "Data Analysis"),
    ]
    job_type = models.CharField(
        max_length=50,
        choices=JOB_POST_TYPES,
        default="Web Development",  # Default job type
    )
    
    JOB_POST_EXPERIENCES = [
        ("less than a year", "less than a year"),
        ("1-2 years", "1-2 years"),
        ("2-3 years", "2-3 years"),
        ("3-4 years", "3-4 years"),
        ("4-5 years", "4-5 years"),
    ]
    experience = models.CharField(
        max_length=50,
        choices=JOB_POST_EXPERIENCES,
        default="4-6 months",  # Default experience
    )
    
    description = models.TextField(blank=True,null=True)
    qualification = models.TextField(blank=True,null=True)
    responsibilities = models.TextField(blank=True,null=True)
    
    JOB_POST_PAYS_CHOICES = [
        ("150,000-250,000", "150,000-250,000"),
        ("250,000-350,000", "250,000-350,000"),
        ("350,000-450,000", "350,000-450,000"),
        ("450,000-550,000", "450,000-550,000"),
        ("650,000-750,000", "650,000-750,000"),
    ]
    pays_range = models.CharField(
        max_length=100,
        choices=JOB_POST_PAYS_CHOICES,
        default="150,000-250,000",  # Default pays range
    )
    
    deadline = models.CharField(max_length=100)
    
    skills = models.ManyToManyField("Skill",related_name="skills_required",blank=True)
    tools = models.ManyToManyField("Tool",related_name="tools_required" ,blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    class Meta:
        indexes = [
            models.Index(fields=["id", "created"])
        ]
        ordering = ["-created"]

class Skill(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(null=True,blank=True)
    client_created = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    
class Tool(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(null=True,blank=True)
    client_created = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name
    