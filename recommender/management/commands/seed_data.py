from django.core.management.base import BaseCommand
from recommender.models import Skill, LearningResource, AssessmentQuestion

class Command(BaseCommand):
    help = 'Seeds initial skills, learning resources, and domain-based assessment questions.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding database with skills, resources, and assessment questions...'))

        # ==========================================
        # 1. SKILLS
        # ==========================================
        skills_data = [
            # Web Development
            {
                'name': 'HTML5 & Modern CSS',
                'category': 'technical',
                'domain': 'web_dev',
                'description': 'Semantic markup, Flexbox, CSS Grid, responsive design principles, and modern layout techniques.',
                'difficulty_level': 'beginner',
                'icon': 'fab fa-html5',
                'market_demand': 'High'
            },
            {
                'name': 'JavaScript (ES6+) & TypeScript',
                'category': 'technical',
                'domain': 'web_dev',
                'description': 'Modern ECMAScript features, asynchronous programming, promises, TypeScript static typing, and browser APIs.',
                'difficulty_level': 'intermediate',
                'icon': 'fab fa-js',
                'market_demand': 'Very High'
            },
            {
                'name': 'React & Frontend Architecture',
                'category': 'technical',
                'domain': 'web_dev',
                'description': 'Hooks, component lifecycles, state management, server components, and responsive single-page web applications.',
                'difficulty_level': 'intermediate',
                'icon': 'fab fa-react',
                'market_demand': 'Very High'
            },
            {
                'name': 'Python & Django Framework',
                'category': 'technical',
                'domain': 'web_dev',
                'description': 'Server-side development with Django ORM, REST framework, authentication, caching, and scalable web services.',
                'difficulty_level': 'intermediate',
                'icon': 'fab fa-python',
                'market_demand': 'Very High'
            },
            {
                'name': 'PostgreSQL & Database Design',
                'category': 'technical',
                'domain': 'web_dev',
                'description': 'Relational data modeling, schema normalization, index optimization, complex queries, and ACID transactions.',
                'difficulty_level': 'intermediate',
                'icon': 'fas fa-database',
                'market_demand': 'Very High'
            },

            # AI & Machine Learning
            {
                'name': 'Python for AI & Data',
                'category': 'technical',
                'domain': 'ai_ml',
                'description': 'NumPy numerical operations, matrix algebra, data transformation, and scientific computing.',
                'difficulty_level': 'beginner',
                'icon': 'fab fa-python',
                'market_demand': 'Very High'
            },
            {
                'name': 'PyTorch & Neural Networks',
                'category': 'technical',
                'domain': 'ai_ml',
                'description': 'Building and training deep neural networks, backpropagation, CNNs, RNNs, and loss optimization.',
                'difficulty_level': 'advanced',
                'icon': 'fas fa-brain',
                'market_demand': 'Very High'
            },
            {
                'name': 'Transformers & Large Language Models',
                'category': 'technical',
                'domain': 'ai_ml',
                'description': 'Attention mechanisms, fine-tuning pretrained transformer models, Hugging Face ecosystem, and tokenization.',
                'difficulty_level': 'advanced',
                'icon': 'fas fa-robot',
                'market_demand': 'Very High'
            },
            {
                'name': 'RAG & Vector Databases',
                'category': 'technical',
                'domain': 'ai_ml',
                'description': 'Retrieval-Augmented Generation, embedding models, semantic search with Chroma/Pinecone, and LLM orchestration.',
                'difficulty_level': 'intermediate',
                'icon': 'fas fa-wand-magic-sparkles',
                'market_demand': 'Very High'
            },
            {
                'name': 'MLOps & Model Deployment',
                'category': 'technical',
                'domain': 'ai_ml',
                'description': 'Model versioning, Dockerization, monitoring drift, FastAPI endpoints, and production inference pipelines.',
                'difficulty_level': 'advanced',
                'icon': 'fas fa-server',
                'market_demand': 'High'
            },

            # Data Science
            {
                'name': 'SQL Analytics & Window Functions',
                'category': 'technical',
                'domain': 'data_science',
                'description': 'Advanced aggregations, windowing functions, CTEs, Cohort analysis, and analytical data marts.',
                'difficulty_level': 'intermediate',
                'icon': 'fas fa-database',
                'market_demand': 'Very High'
            },
            {
                'name': 'Pandas & Data Wrangling',
                'category': 'technical',
                'domain': 'data_science',
                'description': 'Data cleaning, feature transformation, handling missing values, time-series operations, and exploratory analysis.',
                'difficulty_level': 'beginner',
                'icon': 'fas fa-chart-line',
                'market_demand': 'Very High'
            },
            {
                'name': 'Statistical Inference & Hypothesis Testing',
                'category': 'technical',
                'domain': 'data_science',
                'description': 'Probability distributions, p-values, t-tests, ANOVA, regression analysis, and confidence intervals.',
                'difficulty_level': 'intermediate',
                'icon': 'fas fa-chart-pie',
                'market_demand': 'High'
            },

            # Cloud & DevOps
            {
                'name': 'Linux & Shell Scripting',
                'category': 'technical',
                'domain': 'cloud_devops',
                'description': 'Linux file systems, permission management, process monitoring, automation scripts, and SSH workflows.',
                'difficulty_level': 'beginner',
                'icon': 'fab fa-linux',
                'market_demand': 'Very High'
            },
            {
                'name': 'Docker & Containerization',
                'category': 'technical',
                'domain': 'cloud_devops',
                'description': 'Writing efficient Dockerfiles, multi-stage builds, container networking, and docker-compose orchestration.',
                'difficulty_level': 'intermediate',
                'icon': 'fab fa-docker',
                'market_demand': 'Very High'
            },
            {
                'name': 'AWS Cloud Services',
                'category': 'technical',
                'domain': 'cloud_devops',
                'description': 'Core AWS architecture: EC2, S3, IAM security, Lambda serverless, VPC networking, and RDS databases.',
                'difficulty_level': 'intermediate',
                'icon': 'fab fa-aws',
                'market_demand': 'Very High'
            },
            {
                'name': 'CI/CD Pipelines & GitHub Actions',
                'category': 'technical',
                'domain': 'cloud_devops',
                'description': 'Automated testing workflows, artifact packaging, staging deployment, and zero-downtime release pipelines.',
                'difficulty_level': 'intermediate',
                'icon': 'fas fa-code-branch',
                'market_demand': 'Very High'
            },

            # Cybersecurity
            {
                'name': 'Network Security & Packet Analysis',
                'category': 'technical',
                'domain': 'cybersecurity',
                'description': 'TCP/IP architecture, Wireshark packet capture, firewall rules, VPNs, and defense-in-depth security.',
                'difficulty_level': 'beginner',
                'icon': 'fas fa-shield-halved',
                'market_demand': 'Very High'
            },
            {
                'name': 'OWASP Web Application Security',
                'category': 'technical',
                'domain': 'cybersecurity',
                'description': 'Preventing SQL injection, XSS, CSRF, broken access control, and conducting secure code reviews.',
                'difficulty_level': 'intermediate',
                'icon': 'fas fa-bug',
                'market_demand': 'Very High'
            },

            # UI/UX Design
            {
                'name': 'User Research & Journey Mapping',
                'category': 'creative',
                'domain': 'ui_ux',
                'description': 'User interviews, personas, empathy maps, task flow analysis, and identifying core pain points.',
                'difficulty_level': 'beginner',
                'icon': 'fas fa-users-viewfinder',
                'market_demand': 'High'
            },
            {
                'name': 'Figma & Design Systems',
                'category': 'creative',
                'domain': 'ui_ux',
                'description': 'Auto-layout, reusable component tokens, variants, interactive micro-prototypes, and developer handoff.',
                'difficulty_level': 'intermediate',
                'icon': 'fab fa-figma',
                'market_demand': 'Very High'
            },

            # Product Management
            {
                'name': 'Product Strategy & Discovery',
                'category': 'business',
                'domain': 'product_management',
                'description': 'Problem framing, market sizing, value proposition design, and continuous discovery habits.',
                'difficulty_level': 'intermediate',
                'icon': 'fas fa-compass',
                'market_demand': 'Very High'
            },
            {
                'name': 'Agile Sprint Leadership & OKRs',
                'category': 'leadership',
                'domain': 'product_management',
                'description': 'Backlog grooming, sprint cadence, user story mapping, and measurable key result tracking.',
                'difficulty_level': 'intermediate',
                'icon': 'fas fa-bullseye',
                'market_demand': 'High'
            },

            # Soft Skills & Executive Presence
            {
                'name': 'Executive Storytelling & Presentation',
                'category': 'soft',
                'domain': 'soft_skills',
                'description': 'Presenting complex technical concepts to non-technical leaders with clarity, structure, and poise.',
                'difficulty_level': 'intermediate',
                'icon': 'fas fa-microphone-lines',
                'market_demand': 'Very High'
            },
            {
                'name': 'Salary Negotiation & Career Advocacy',
                'category': 'leadership',
                'domain': 'soft_skills',
                'description': 'Advocating for promotions, strategic salary negotiation, boundary setting, and building a sponsor network.',
                'difficulty_level': 'intermediate',
                'icon': 'fas fa-handshake',
                'market_demand': 'Very High'
            },

            # General Cross-Cutting Skills
            {
                'name': 'Git & Collaborative Version Control',
                'category': 'technical',
                'domain': 'general',
                'description': 'Branching strategies, resolving merge conflicts, pull request reviews, and open source collaboration.',
                'difficulty_level': 'beginner',
                'icon': 'fab fa-git-alt',
                'market_demand': 'Very High'
            },
        ]

        created_skills = {}
        for s_data in skills_data:
            skill_obj, created = Skill.objects.update_or_create(
                name=s_data['name'],
                defaults=s_data
            )
            created_skills[skill_obj.name] = skill_obj

        self.stdout.write(self.style.SUCCESS(f"Populated {len(created_skills)} skills across all domains."))

        # ==========================================
        # 2. LEARNING RESOURCES
        # ==========================================
        resources_data = [
            # Web Dev
            {
                'skill_name': 'HTML5 & Modern CSS',
                'title': 'MDN Web Docs: Modern Web Development Curriculum',
                'description': 'Comprehensive guides covering semantic HTML5, Flexbox, CSS Grid, and responsive web principles.',
                'resource_type': 'tutorial',
                'url': 'https://developer.mozilla.org/en-US/docs/Learn',
                'provider': 'Mozilla Developer Network',
                'difficulty_level': 'beginner',
                'rating': 4.9,
                'duration_hours': 25.0,
                'is_free': True
            },
            {
                'skill_name': 'JavaScript (ES6+) & TypeScript',
                'title': 'The Modern JavaScript Tutorial (javascript.info)',
                'description': 'In-depth coverage from JS fundamentals to advanced closures, promises, event loop, and TypeScript.',
                'resource_type': 'course',
                'url': 'https://javascript.info/',
                'provider': 'JavaScript.info',
                'difficulty_level': 'intermediate',
                'rating': 4.9,
                'duration_hours': 35.0,
                'is_free': True
            },
            {
                'skill_name': 'React & Frontend Architecture',
                'title': 'Full Stack Open - Deep Dive Into Modern Web Development',
                'description': 'University of Helsinki free accredited course covering React, Redux, Node.js, and modern TypeScript architecture.',
                'resource_type': 'course',
                'url': 'https://fullstackopen.com/en/',
                'provider': 'University of Helsinki',
                'difficulty_level': 'intermediate',
                'rating': 5.0,
                'duration_hours': 60.0,
                'is_free': True
            },
            {
                'skill_name': 'Python & Django Framework',
                'title': 'CS50 Web Programming with Python and JavaScript',
                'description': 'Harvard University premier introduction to web apps, databases, Django ORM, and scalability.',
                'resource_type': 'course',
                'url': 'https://cs50.harvard.edu/web/',
                'provider': 'Harvard University',
                'difficulty_level': 'intermediate',
                'rating': 4.9,
                'duration_hours': 45.0,
                'is_free': True
            },
            {
                'skill_name': 'PostgreSQL & Database Design',
                'title': 'PostgreSQL Tutorial & High-Performance Query Optimization',
                'description': 'Mastering relational design, transactions, indexing, and window functions.',
                'resource_type': 'tutorial',
                'url': 'https://www.postgresqltutorial.com/',
                'provider': 'PostgreSQL Guide',
                'difficulty_level': 'intermediate',
                'rating': 4.8,
                'duration_hours': 15.0,
                'is_free': True
            },

            # AI & ML
            {
                'skill_name': 'Python for AI & Data',
                'title': 'Python for Data Analysis & Scientific Computing',
                'description': 'Complete guide to vectorized calculations, NumPy arrays, and linear operations.',
                'resource_type': 'book',
                'url': 'https://wesmckinney.com/book/',
                'provider': "O'Reilly Media (Free Online)",
                'difficulty_level': 'beginner',
                'rating': 4.9,
                'duration_hours': 20.0,
                'is_free': True
            },
            {
                'skill_name': 'PyTorch & Neural Networks',
                'title': 'Practical Deep Learning for Coders',
                'description': 'World-renowned Fast.ai deep learning program by Jeremy Howard emphasizing top-down intuitive learning.',
                'resource_type': 'course',
                'url': 'https://course.fast.ai/',
                'provider': 'Fast.ai',
                'difficulty_level': 'intermediate',
                'rating': 5.0,
                'duration_hours': 40.0,
                'is_free': True
            },
            {
                'skill_name': 'Transformers & Large Language Models',
                'title': 'Hugging Face NLP & Transformer Course',
                'description': 'Official hands-on curriculum for fine-tuning BERT, GPT, and modern transformer architectures.',
                'resource_type': 'course',
                'url': 'https://huggingface.co/learn/nlp-course',
                'provider': 'Hugging Face',
                'difficulty_level': 'advanced',
                'rating': 4.9,
                'duration_hours': 30.0,
                'is_free': True
            },
            {
                'skill_name': 'RAG & Vector Databases',
                'title': 'Building Production RAG Systems with LangChain & LlamaIndex',
                'description': 'Step-by-step masterclass on chunking, vector indexing, reranking, and semantic retrieval.',
                'resource_type': 'tutorial',
                'url': 'https://www.deeplearning.ai/short-courses/',
                'provider': 'DeepLearning.AI',
                'difficulty_level': 'intermediate',
                'rating': 4.8,
                'duration_hours': 10.0,
                'is_free': True
            },

            # Cloud & DevOps
            {
                'skill_name': 'Docker & Containerization',
                'title': 'Docker Curriculum: A Hands-on Container Masterclass',
                'description': 'Comprehensive hands-on guide for containerizing full-stack microservices and deployment.',
                'resource_type': 'tutorial',
                'url': 'https://docker-curriculum.com/',
                'provider': 'Docker Community',
                'difficulty_level': 'beginner',
                'rating': 4.9,
                'duration_hours': 12.0,
                'is_free': True
            },
            {
                'skill_name': 'AWS Cloud Services',
                'title': 'AWS Cloud Practitioner & Solutions Architect Foundations',
                'description': 'Free Tier hands-on labs covering compute, storage, networking, and cloud security.',
                'resource_type': 'course',
                'url': 'https://aws.amazon.com/training/digital/',
                'provider': 'AWS Skill Builder',
                'difficulty_level': 'intermediate',
                'rating': 4.8,
                'duration_hours': 25.0,
                'is_free': True
            },

            # Soft Skills
            {
                'skill_name': 'Salary Negotiation & Career Advocacy',
                'title': 'Ask A Manager: Women in Leadership & Negotiation Guide',
                'description': 'Practical frameworks and scripts for negotiating compensation, setting boundaries, and claiming achievements.',
                'resource_type': 'article',
                'url': 'https://www.askamanager.org/',
                'provider': 'Alison Green Leadership',
                'difficulty_level': 'intermediate',
                'rating': 4.9,
                'duration_hours': 6.0,
                'is_free': True
            },
            {
                'skill_name': 'Git & Collaborative Version Control',
                'title': 'Pro Git Book (Official Free Edition)',
                'description': 'The definitive guide to Git internals, branching, rebasing, and collaborative team workflows.',
                'resource_type': 'book',
                'url': 'https://git-scm.com/book/en/v2',
                'provider': 'Git SCM',
                'difficulty_level': 'beginner',
                'rating': 4.9,
                'duration_hours': 18.0,
                'is_free': True
            }
        ]

        for r_data in resources_data:
            skill = created_skills.get(r_data['skill_name'])
            if skill:
                LearningResource.objects.update_or_create(
                    title=r_data['title'],
                    defaults={
                        'description': r_data['description'],
                        'resource_type': r_data['resource_type'],
                        'url': r_data['url'],
                        'skill': skill,
                        'provider': r_data['provider'],
                        'difficulty_level': r_data['difficulty_level'],
                        'rating': r_data['rating'],
                        'duration_hours': r_data['duration_hours'],
                        'is_free': r_data['is_free']
                    }
                )

        self.stdout.write(self.style.SUCCESS(f"Populated {len(resources_data)} verified learning resources."))

        # ==========================================
        # 3. DOMAIN-SPECIFIC ASSESSMENT QUESTIONS
        # ==========================================
        questions_data = [
            # Web Development Questions
            {
                'domain': 'web_dev',
                'skill_name': 'React & Frontend Architecture',
                'question_text': 'When optimizing a React application with frequent re-renders caused by parent prop changes, which hook or technique memoizes expensive computed values across renders?',
                'option_a': 'useEffect hook with an empty dependency array',
                'option_b': 'useMemo hook specifying the relevant calculation inputs as dependencies',
                'option_c': 'useRef hook attached directly to DOM elements',
                'option_d': 'useLayoutEffect hook before browser paint',
                'correct_option': 'b',
                'explanation': 'useMemo memoizes the result of an expensive calculation and only recalculates when one of its specified dependencies changes.',
                'difficulty': 'intermediate'
            },
            {
                'domain': 'web_dev',
                'skill_name': 'Python & Django Framework',
                'question_text': 'In Django ORM, how do you prevent the "N+1 query problem" when retrieving a list of blog posts along with their single author User object?',
                'option_a': 'Using BlogPost.objects.all().prefetch_related("author")',
                'option_b': 'Using BlogPost.objects.all().select_related("author")',
                'option_c': 'Using BlogPost.objects.raw("SELECT * FROM post")',
                'option_d': 'Using BlogPost.objects.filter(author__isnull=False)',
                'correct_option': 'b',
                'explanation': 'select_related performs an SQL JOIN and includes the related OneToOne or ForeignKey fields in a single query.',
                'difficulty': 'intermediate'
            },
            {
                'domain': 'web_dev',
                'skill_name': 'JavaScript (ES6+) & TypeScript',
                'question_text': 'What will be the output order of: console.log("A"); setTimeout(() => console.log("B"), 0); Promise.resolve().then(() => console.log("C")); console.log("D"); ?',
                'option_a': 'A, B, C, D',
                'option_b': 'A, D, C, B',
                'option_c': 'A, C, D, B',
                'option_d': 'A, D, B, C',
                'correct_option': 'b',
                'explanation': 'Synchronous code runs first (A, D), followed by the microtask queue (Promise C), and finally the macrotask queue (setTimeout B).',
                'difficulty': 'advanced'
            },

            # AI & Machine Learning Questions
            {
                'domain': 'ai_ml',
                'skill_name': 'PyTorch & Neural Networks',
                'question_text': 'Your deep neural network achieves 99% accuracy on training data but drops to 62% accuracy on validation data. What phenomenon is happening, and which regularization strategy directly mitigates it?',
                'option_a': 'Underfitting; increase model depth and epochs',
                'option_b': 'Overfitting; apply Dropout layers, weight decay (L2), or data augmentation',
                'option_c': 'Vanishing gradient; use Sigmoid activation functions',
                'option_d': 'Exploding gradient; remove batch normalization layers',
                'correct_option': 'b',
                'explanation': 'High training accuracy paired with poor validation accuracy indicates overfitting, where the network memorizes noise. Dropout and L2 regularization prevent co-adaptation.',
                'difficulty': 'intermediate'
            },
            {
                'domain': 'ai_ml',
                'skill_name': 'Transformers & Large Language Models',
                'question_text': 'What core architectural mechanism enables Transformer models (like GPT and BERT) to process all input tokens in parallel rather than sequentially?',
                'option_a': 'Recurrent feedback loops',
                'option_b': 'Multi-Head Self-Attention mechanisms with positional encodings',
                'option_c': 'Convolutional max-pooling filters',
                'option_d': 'Markov chain state transitions',
                'correct_option': 'b',
                'explanation': 'Multi-head self-attention computes relationships between every token in the sequence simultaneously, eliminating the sequential bottleneck of RNNs.',
                'difficulty': 'intermediate'
            },
            {
                'domain': 'ai_ml',
                'skill_name': 'RAG & Vector Databases',
                'question_text': 'In a Retrieval-Augmented Generation (RAG) architecture, what is the primary role of an embedding model?',
                'option_a': 'To compress the text file into a zip archive',
                'option_b': 'To translate text from foreign languages into English',
                'option_c': 'To convert text chunks into dense mathematical vector representations capturing semantic meaning',
                'option_d': 'To execute unit tests on the retrieved documents',
                'correct_option': 'c',
                'explanation': 'Embedding models convert text chunks into high-dimensional vector spaces where semantically similar concepts reside near one another via cosine similarity.',
                'difficulty': 'intermediate'
            },

            # Data Science Questions
            {
                'domain': 'data_science',
                'skill_name': 'SQL Analytics & Window Functions',
                'question_text': 'Which SQL clause calculates a running total of revenue ordered by transaction date without collapsing rows like a GROUP BY would?',
                'option_a': 'SUM(revenue) OVER (ORDER BY transaction_date)',
                'option_b': 'SUM(revenue) GROUP BY transaction_date',
                'option_c': 'TOTAL(revenue) WHERE transaction_date IS NOT NULL',
                'option_d': 'COUNT(revenue) HAVING transaction_date > NOW()',
                'correct_option': 'a',
                'explanation': 'The OVER (ORDER BY ...) window clause computes aggregate values across a partitioned or ordered set while maintaining original row granularity.',
                'difficulty': 'intermediate'
            },
            {
                'domain': 'data_science',
                'skill_name': 'Statistical Inference & Hypothesis Testing',
                'question_text': 'In an A/B test for a new landing page conversion, what does a p-value of 0.02 (at significance level alpha = 0.05) indicate?',
                'option_a': 'There is only a 2% chance that the new landing page is better',
                'option_b': 'The result is statistically significant; reject the null hypothesis that there is no difference',
                'option_c': 'The test is invalid and must be rerun with larger sample sizes',
                'option_d': 'The conversion rate improved by exactly 2%',
                'correct_option': 'b',
                'explanation': 'Since p (0.02) < alpha (0.05), we reject the null hypothesis and conclude that the observed conversion difference is statistically significant.',
                'difficulty': 'intermediate'
            },

            # Cloud & DevOps Questions
            {
                'domain': 'cloud_devops',
                'skill_name': 'Docker & Containerization',
                'question_text': 'Why are multi-stage builds recommended when authoring production Dockerfiles for web applications?',
                'option_a': 'They permit multiple operating systems to run inside a single container',
                'option_b': 'They isolate build dependencies (compilers, SDKs) and produce lightweight, secure runtime images',
                'option_c': 'They automatically restart containers upon unexpected crashes',
                'option_d': 'They bypass Docker image layer caching',
                'correct_option': 'b',
                'explanation': 'Multi-stage builds leave behind heavy build tools, SDKs, and source artifacts, creating minimal and secure production images.',
                'difficulty': 'intermediate'
            },
            {
                'domain': 'cloud_devops',
                'skill_name': 'AWS Cloud Services',
                'question_text': 'Which AWS service is designed to distribute incoming application network traffic across multiple EC2 targets in multiple Availability Zones?',
                'option_a': 'Amazon Route 53',
                'option_b': 'Elastic Load Balancing (Application Load Balancer)',
                'option_c': 'AWS Auto Scaling Group',
                'option_d': 'Amazon CloudFront CDN',
                'correct_option': 'b',
                'explanation': 'Application Load Balancer (ALB) automatically distributes incoming HTTP/HTTPS traffic across targets in multiple availability zones.',
                'difficulty': 'beginner'
            },

            # Cybersecurity Questions
            {
                'domain': 'cybersecurity',
                'skill_name': 'OWASP Web Application Security',
                'question_text': 'What is the most effective primary defense against SQL Injection vulnerabilities in backend web applications?',
                'option_a': 'Validating client-side input in JavaScript only',
                'option_b': 'Using parameterized queries / prepared statements via ORMs rather than string concatenation',
                'option_c': 'Encrypting database passwords with MD5 hashing',
                'option_d': 'Hiding the database port number behind NAT',
                'correct_option': 'b',
                'explanation': 'Parameterized queries separate SQL code from untrusted data parameters, ensuring user input is never interpreted as executable SQL statements.',
                'difficulty': 'beginner'
            },

            # UI/UX Questions
            {
                'domain': 'ui_ux',
                'skill_name': 'Figma & Design Systems',
                'question_text': 'In design system token architecture, what is the best practice for decoupling semantic intent from raw color values?',
                'option_a': 'Hardcoding hex codes directly in every UI component',
                'option_b': 'Layering Design Tokens: Global tokens (e.g., blue-500) map to Semantic tokens (e.g., color-primary-interactive)',
                'option_c': 'Using bitmap PNG icons instead of SVG vectors',
                'option_d': 'Creating unique styles for every individual screen',
                'correct_option': 'b',
                'explanation': 'Token layering allows theming, dark mode switches, and brand updates by simply altering semantic token aliases without touching component templates.',
                'difficulty': 'intermediate'
            },

            # Soft Skills Questions
            {
                'domain': 'soft_skills',
                'skill_name': 'Executive Storytelling & Presentation',
                'question_text': 'When presenting a technical proposal to executive stakeholders (VPs/C-suite), which communication structure delivers maximum impact?',
                'option_a': 'Chronological narrative explaining every step taken in the last 6 months first',
                'option_b': 'Pyramid Principle / Bottom-line up front: Start with the recommendation and business impact, then supporting pillars',
                'option_c': 'Showing 50 slides filled with raw terminal logs and error dumps',
                'option_d': 'Avoiding all numbers, metrics, and business outcomes',
                'correct_option': 'b',
                'explanation': 'Executive audiences need conclusions first (the synthesis/recommendation), followed by business impact, followed by technical feasibility details.',
                'difficulty': 'intermediate'
            }
        ]

        for q_data in questions_data:
            skill = created_skills.get(q_data.get('skill_name'))
            AssessmentQuestion.objects.update_or_create(
                question_text=q_data['question_text'],
                defaults={
                    'domain': q_data['domain'],
                    'skill': skill,
                    'option_a': q_data['option_a'],
                    'option_b': q_data['option_b'],
                    'option_c': q_data['option_c'],
                    'option_d': q_data['option_d'],
                    'correct_option': q_data['correct_option'],
                    'explanation': q_data['explanation'],
                    'difficulty': q_data['difficulty'],
                }
            )

        self.stdout.write(self.style.SUCCESS(f"Populated {len(questions_data)} scenario assessment questions."))
        self.stdout.write(self.style.SUCCESS("Database seeding complete!"))
