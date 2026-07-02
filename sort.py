import json
import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
from tqdm import tqdm

# ============================================================
# CONFIGURATION
# ============================================================

INPUT_FILE = "candidates.jsonl"
OUTPUT_FILE = "sorted_candidates.jsonl"

# Lower number = higher priority
CATEGORY_PRIORITY = {

    # ======================================================
    # AI / DATA
    # ======================================================
    "AI_ML": 1,
    "DATA_SCIENCE": 2,
    "DATA_ENGINEER": 3,
    "DATA_ANALYST": 4,
    "BUSINESS_ANALYST": 5,

    # ======================================================
    # SOFTWARE DEVELOPMENT
    # ======================================================
    "SOFTWARE_ENGINEER": 6,
    "FULL_STACK": 7,
    "BACKEND": 8,
    "FRONTEND": 9,
    "MOBILE": 10,

    # ======================================================
    # CLOUD / DEVOPS / SECURITY
    # ======================================================
    "DEVOPS_CLOUD": 11,
    "CYBER_SECURITY": 12,
    "DATABASE": 13,
    "QA_TESTING": 14,
    "EMBEDDED": 15,
    "BLOCKCHAIN": 16,
    "GAME_DEV": 17,

    # ======================================================
    # CORE ENGINEERING
    # ======================================================
    "ROBOTICS": 18,
    "MECHANICAL": 19,
    "ELECTRICAL": 20,
    "CIVIL": 21,
    "CHEMICAL": 22,
    "AEROSPACE": 23,

    # ======================================================
    # DESIGN
    # ======================================================
    "UI_UX": 24,
    "GRAPHIC_DESIGN": 25,

    # ======================================================
    # MANAGEMENT
    # ======================================================
    "PRODUCT": 26,
    "PROJECT_MANAGER": 27,
    "PROGRAM_MANAGER": 28,

    # ======================================================
    # BUSINESS
    # ======================================================
    "OPERATIONS": 29,
    "SALES": 30,
    "MARKETING": 31,
    "FINANCE": 32,
    "HR": 33,
    "CUSTOMER_SUPPORT": 34,

    # ======================================================
    # ENTERPRISE
    # ======================================================
    "SUPPLY_CHAIN": 35,
    "BANKING": 36,
    "LEGAL": 37,
    "CONTENT": 38,

    # ======================================================
    # HEALTHCARE / EDUCATION
    # ======================================================
    "HEALTHCARE": 39,
    "EDUCATION": 40,

    # ======================================================
    # SPECIALIZED
    # ======================================================
    "TELECOM": 41,
    "GIS": 42,
    "ARCHITECTURE": 43,
    "MEDIA": 44,
    "SCIENCE": 45,

    # ======================================================
    # UNKNOWN
    # ======================================================
    "OTHER": 999

}
# ============================================================
# KEYWORDS
# ============================================================
ROLE_KEYWORDS = {

# ==========================================================
# AI / MACHINE LEARNING
# ==========================================================

"AI_ML":[

# Artificial Intelligence
"ai",
"ai engineer",
"senior ai engineer",
"lead ai engineer",
"principal ai engineer",
"staff ai engineer",
"associate ai engineer",
"artificial intelligence",
"artificial intelligence engineer",
"artificial intelligence developer",
"artificial intelligence architect",
"ai consultant",
"ai specialist",
"ai developer",
"ai architect",
"ai researcher",
"ai research engineer",
"ai research scientist",
"ai scientist",
"applied ai engineer",
"applied ai scientist",

# Machine Learning
"machine learning",
"machine learning engineer",
"senior machine learning engineer",
"lead machine learning engineer",
"principal machine learning engineer",
"staff machine learning engineer",
"associate machine learning engineer",
"junior machine learning engineer",
"machine learning developer",
"machine learning scientist",
"machine learning architect",

"ml engineer",
"senior ml engineer",
"lead ml engineer",
"staff ml engineer",
"principal ml engineer",
"associate ml engineer",
"junior ml engineer",
"ml developer",
"ml scientist",
"ml architect",
"ml consultant",

# Applied ML
"applied scientist",
"senior applied scientist",
"principal applied scientist",
"staff applied scientist",
"research scientist",
"research engineer",
"ai research",
"ml research",

# Deep Learning
"deep learning",
"deep learning engineer",
"deep learning scientist",

# NLP
"nlp",
"nlp engineer",
"senior nlp engineer",
"language engineer",
"language model engineer",
"natural language processing",
"computational linguist",

# LLM
"llm",
"llm engineer",
"llm developer",
"foundation model",
"foundation model engineer",
"foundation model researcher",
"large language model",
"prompt engineer",
"prompt engineering",
"generative ai",
"gen ai",
"genai",
"rag",
"retrieval augmented generation",
"langchain",
"llamaindex",
"agentic ai",
"ai agent engineer",
"multi agent systems",

# Vision
"computer vision",
"computer vision engineer",
"computer vision scientist",
"vision engineer",
"image processing",
"ocr engineer",
"video analytics",

# Recommendation
"recommendation systems",
"recommendation system",
"recommendation engineer",
"recommendation systems engineer",
"recommendation scientist",
"recommendation specialist",
"recommendation platform",
"recommender systems",

# Search
"search engineer",
"search relevance",
"ranking engineer",
"ranking scientist",
"retrieval engineer",
"semantic retrieval",
"semantic search",
"search platform",

# Embeddings
"embedding engineer",
"embedding models",
"vector search",
"vector database",
"vector retrieval",

# MLOps
"mlops",
"ml ops",
"machine learning operations",
"model deployment",
"model serving",
"model optimization",
"model monitoring",
"feature engineering",
"feature store",
"feature pipeline",

# Frameworks
"tensorflow",
"pytorch",
"keras",
"huggingface",
"transformers",
"onnx",
"torchserve",

# AI Infrastructure
"inference engineer",
"inference optimization",
"gpu optimization",
"distributed training",
"model compression",
"quantization"

],

# ==========================================================
# DATA SCIENCE
# ==========================================================

"DATA_SCIENCE":[

"data scientist",
"senior data scientist",
"lead data scientist",
"principal data scientist",
"staff data scientist",
"associate data scientist",
"junior data scientist",

"decision scientist",
"analytics scientist",
"quantitative scientist",
"research scientist",
"statistical scientist",

"predictive analytics",
"predictive modeling",
"statistical modeling",

"forecasting",
"time series analyst",
"time series forecasting",

"experimentation",
"ab testing",
"a/b testing",

"causal inference",

"bayesian modeling",

"operations research",

"optimization scientist",

"data science consultant",

"research analyst"

],

# ==========================================================
# DATA ENGINEERING
# ==========================================================

"DATA_ENGINEER":[

"data engineer",
"senior data engineer",
"lead data engineer",
"principal data engineer",
"staff data engineer",
"associate data engineer",

"big data engineer",

"etl engineer",
"etl developer",

"data platform engineer",
"platform engineer",

"pipeline engineer",
"data pipeline",

"data warehouse engineer",

"data integration",

"spark engineer",
"hadoop engineer",

"snowflake engineer",

"airflow",

"databricks",

"delta lake",

"lakehouse",

"azure data engineer",

"aws data engineer",

"gcp data engineer",

"streaming engineer",

"kafka engineer",

"flink",

"data infrastructure"

],

# ==========================================================
# DATA ANALYST
# ==========================================================

"DATA_ANALYST":[

"data analyst",
"senior data analyst",
"lead data analyst",
"junior data analyst",

"analytics engineer",

"analytics consultant",

"analytics associate",

"report analyst",

"reporting analyst",

"reporting specialist",

"business intelligence",

"business intelligence analyst",

"bi analyst",

"bi developer",

"power bi",

"tableau",

"dashboard developer",

"dashboard analyst",

"mis analyst",

"mis executive",

"sql analyst",

"reporting executive",

"insights analyst",

"decision analyst",

"data visualization",

"visualization analyst"

],

# ==========================================================
# BUSINESS ANALYST
# ==========================================================

"BUSINESS_ANALYST":[

"business analyst",
"senior business analyst",
"lead business analyst",

"business systems analyst",

"business process analyst",

"functional analyst",

"erp analyst",

"sap analyst",

"oracle functional consultant",

"consultant",

"process analyst",

"requirement analyst",

"requirements engineer",

"process consultant",

"operations analyst",

"strategy analyst",

"business consultant",

"product analyst",

"crm consultant",

"implementation consultant"

],
# ==========================================================
# SOFTWARE ENGINEERING
# ==========================================================

"SOFTWARE_ENGINEER":[

"software engineer",
"senior software engineer",
"lead software engineer",
"principal software engineer",
"staff software engineer",
"associate software engineer",
"junior software engineer",

"software developer",
"application developer",
"application engineer",
"software consultant",
"software programmer",

"sde",
"sde i",
"sde ii",
"sde iii",
"sde-1",
"sde-2",
"sde-3",

"member of technical staff",
"mts",

"technical lead",
"tech lead",

"engineering lead",

],

# ==========================================================
# BACKEND
# ==========================================================

"BACKEND":[

"backend engineer",
"backend developer",
"backend software engineer",
"backend architect",

"python developer",
"django developer",
"flask developer",
"fastapi developer",

"java developer",
"spring developer",
"spring boot developer",

"node developer",
"nodejs developer",
"node.js developer",
"express developer",

"golang developer",
"go developer",

"php developer",
"laravel developer",

"ruby developer",
"rails developer",

"scala developer",

"c++ developer",
"c developer",

"api developer",

"microservices engineer",

"distributed systems engineer",

],

# ==========================================================
# FRONTEND
# ==========================================================

"FRONTEND":[

"frontend engineer",
"frontend developer",

"react developer",
"react engineer",
"reactjs developer",

"angular developer",

"vue developer",

"javascript developer",

"typescript developer",

"web developer",

"ui developer",

"frontend architect",

],

# ==========================================================
# FULL STACK
# ==========================================================

"FULL_STACK":[

"full stack developer",
"full stack engineer",
"full stack software engineer",

"fullstack developer",
"fullstack engineer",

"mern developer",
"mern stack developer",

"mean developer",
"mean stack developer",

],

# ==========================================================
# DEVOPS
# ==========================================================

"DEVOPS_CLOUD":[

"devops engineer",
"senior devops engineer",
"lead devops engineer",

"cloud engineer",

"cloud architect",

"aws engineer",
"aws architect",

"azure engineer",
"azure architect",

"gcp engineer",

"site reliability engineer",
"sre",

"platform engineer",

"infrastructure engineer",

"kubernetes",

"docker",

"terraform",

"ansible",

"jenkins",

"argo cd",

"gitops",

"linux engineer",

],

# ==========================================================
# CYBER SECURITY
# ==========================================================

"CYBER_SECURITY":[

"cyber security",

"cybersecurity engineer",

"security engineer",

"security analyst",

"soc analyst",

"penetration tester",

"ethical hacker",

"red team",

"blue team",

"security consultant",

"cloud security",

"application security",

"devsecops",

"iam engineer",

],

# ==========================================================
# QA / TESTING
# ==========================================================

"QA_TESTING":[

"qa engineer",

"quality assurance engineer",

"software tester",

"test engineer",

"automation tester",

"automation engineer",

"sdet",

"manual tester",

"performance tester",

"load tester",

"test automation",

],

# ==========================================================
# DATABASE
# ==========================================================

"DATABASE":[

"database administrator",

"dba",

"database engineer",

"database developer",

"sql developer",

"oracle developer",

"mysql",

"postgresql",

"mongodb",

"cassandra",

"redis",

"database architect",

],

# ==========================================================
# MOBILE
# ==========================================================

"MOBILE":[

"android developer",

"android engineer",

"ios developer",

"ios engineer",

"mobile developer",

"mobile engineer",

"flutter developer",

"flutter engineer",

"react native developer",

"react native engineer",

"kotlin developer",

"swift developer",

"xamarin",

],

# ==========================================================
# EMBEDDED / IOT
# ==========================================================

"EMBEDDED":[

"embedded engineer",

"embedded software engineer",

"embedded developer",

"firmware engineer",

"firmware developer",

"embedded systems",

"electronics engineer",

"hardware engineer",

"pcb designer",

"iot engineer",

"internet of things",

"rtos",

"microcontroller",

"stm32",

"arduino",

"raspberry pi",

],

# ==========================================================
# BLOCKCHAIN
# ==========================================================

"BLOCKCHAIN":[

"blockchain developer",

"blockchain engineer",

"web3 developer",

"smart contract engineer",

"solidity developer",

"ethereum developer",

"hyperledger",

"rust blockchain",

],

# ==========================================================
# GAME DEVELOPMENT
# ==========================================================

"GAME_DEV":[

"game developer",

"game engineer",

"unity developer",

"unity engineer",

"unreal developer",

"unreal engine",

"graphics programmer",

"gameplay programmer",

],
# ==========================================================
# MECHANICAL ENGINEERING
# ==========================================================

"MECHANICAL":[

"mechanical engineer",
"senior mechanical engineer",
"lead mechanical engineer",
"associate mechanical engineer",
"junior mechanical engineer",

"mechanical design engineer",
"design engineer",

"cad engineer",
"cad designer",

"solidworks designer",
"catia designer",
"autocad designer",
"creo engineer",
"nx cad engineer",

"manufacturing engineer",

"production engineer",

"maintenance engineer",

"industrial engineer",

"quality engineer",

"quality control engineer",

"process engineer",

"tool design engineer",

"tooling engineer",

"plant engineer",

"assembly engineer",

"automotive engineer",

"thermal engineer",

"hvac engineer",

"piping engineer",

"rotating equipment engineer",

"static equipment engineer",

"reliability engineer",

"field engineer"

],

# ==========================================================
# CIVIL ENGINEERING
# ==========================================================

"CIVIL":[

"civil engineer",

"structural engineer",

"construction engineer",

"site engineer",

"project engineer",

"planning engineer",

"quantity surveyor",

"billing engineer",

"estimation engineer",

"bridge engineer",

"geotechnical engineer",

"transportation engineer",

"water resources engineer",

"highway engineer",

"resident engineer",

"contracts engineer"

],

# ==========================================================
# ELECTRICAL
# ==========================================================

"ELECTRICAL":[

"electrical engineer",

"electronics engineer",

"electrical design engineer",

"power systems engineer",

"power engineer",

"substation engineer",

"protection engineer",

"control engineer",

"instrumentation engineer",

"electrical maintenance engineer",

"electrical project engineer",

"automation engineer",

"plc engineer",

"scada engineer",

"vlsi engineer",

"asic engineer",

"digital design engineer",

"analog design engineer"

],

# ==========================================================
# ROBOTICS
# ==========================================================

"ROBOTICS":[

"robotics engineer",

"robotics developer",

"robotics software engineer",

"robotics researcher",

"autonomous systems engineer",

"automation engineer",

"ros engineer",

"ros2",

"slam engineer",

"path planning",

"motion planning"

],

# ==========================================================
# AEROSPACE
# ==========================================================

"AEROSPACE":[

"aerospace engineer",

"aircraft engineer",

"aviation engineer",

"flight systems engineer",

"propulsion engineer",

"aerodynamics engineer",

"space systems engineer",

"satellite engineer"

],

# ==========================================================
# CHEMICAL
# ==========================================================

"CHEMICAL":[

"chemical engineer",

"process chemist",

"process engineer",

"petroleum engineer",

"refinery engineer",

"oil and gas engineer",

"polymer engineer",

"pharmaceutical engineer"

],

# ==========================================================
# HR
# ==========================================================

"HR":[

"human resources",

"human resource",

"hr executive",

"hr manager",

"hr generalist",

"hr business partner",

"talent acquisition",

"talent partner",

"technical recruiter",

"recruiter",

"senior recruiter",

"campus recruiter",

"sourcing specialist",

"people operations",

"people partner",

"hr operations"

],

# ==========================================================
# SALES
# ==========================================================

"SALES":[

"sales executive",

"sales engineer",

"sales manager",

"regional sales manager",

"territory sales manager",

"inside sales",

"outside sales",

"business development",

"business development executive",

"business development manager",

"account executive",

"account manager",

"sales consultant",

"relationship manager",

"channel sales",

"pre sales",

"solution consultant"

],

# ==========================================================
# MARKETING
# ==========================================================

"MARKETING":[

"marketing manager",

"digital marketing",

"digital marketing manager",

"marketing executive",

"brand manager",

"growth manager",

"growth marketing",

"performance marketing",

"seo",

"seo specialist",

"sem",

"ppc specialist",

"content marketing",

"email marketing",

"affiliate marketing",

"social media manager",

"social media marketing",

"marketing analyst"

],

# ==========================================================
# FINANCE
# ==========================================================

"FINANCE":[

"accountant",

"senior accountant",

"chartered accountant",

"finance manager",

"finance analyst",

"financial analyst",

"investment analyst",

"equity analyst",

"credit analyst",

"risk analyst",

"audit",

"auditor",

"internal auditor",

"tax consultant",

"tax analyst",

"cost accountant",

"accounts payable",

"accounts receivable"

],

# ==========================================================
# CUSTOMER SUPPORT
# ==========================================================

"CUSTOMER_SUPPORT":[

"customer support",

"customer support executive",

"customer support engineer",

"customer service",

"customer service executive",

"customer success",

"customer success manager",

"customer success engineer",

"technical support",

"technical support engineer",

"support engineer",

"application support",

"help desk",

"helpdesk",

"service desk",

"it support",

"client support",

"chat support",

"voice support",

"non voice",

"call center",

"contact center"

],

# ==========================================================
# OPERATIONS
# ==========================================================

"OPERATIONS":[

"operations manager",

"operations executive",

"operations analyst",

"operations associate",

"operations coordinator",

"business operations",

"program operations",

"supply operations",

"logistics coordinator",

"warehouse manager",

"inventory analyst",

"inventory manager"

],

# ==========================================================
# CONTENT
# ==========================================================

"CONTENT":[

"content writer",

"technical writer",

"copywriter",

"content strategist",

"content editor",

"documentation engineer",

"documentation specialist",

"editor",

"proofreader"

],
# ==========================================================
# HEALTHCARE / MEDICAL
# ==========================================================

"HEALTHCARE":[

"doctor",
"physician",
"medical officer",
"resident doctor",
"surgeon",
"dentist",
"pharmacist",
"clinical pharmacist",
"clinical research associate",
"clinical research coordinator",
"medical writer",
"medical coder",
"medical officer",
"medical representative",
"nurse",
"staff nurse",
"registered nurse",
"physiotherapist",
"radiologist",
"pathologist",
"lab technician",
"laboratory technician",
"microbiologist",
"biotechnologist",
"biomedical engineer",
"public health specialist",
"healthcare consultant"

],

# ==========================================================
# EDUCATION
# ==========================================================

"EDUCATION":[

"teacher",
"assistant professor",
"associate professor",
"professor",
"lecturer",
"faculty",
"trainer",
"instructor",
"teaching assistant",
"research assistant",
"research associate",
"education counselor",
"academic coordinator",
"curriculum developer"

],

# ==========================================================
# LEGAL
# ==========================================================

"LEGAL":[

"lawyer",
"advocate",
"legal advisor",
"legal associate",
"legal counsel",
"corporate lawyer",
"litigation associate",
"compliance officer",
"compliance analyst",
"contract specialist",
"contract manager",
"company secretary"

],

# ==========================================================
# BANKING
# ==========================================================

"BANKING":[

"bank manager",
"relationship manager",
"relationship officer",
"credit manager",
"loan officer",
"investment banker",
"private banker",
"wealth manager",
"insurance advisor",
"insurance manager",
"insurance specialist",
"claims analyst",
"claims manager"

],

# ==========================================================
# SUPPLY CHAIN
# ==========================================================

"SUPPLY_CHAIN":[

"supply chain manager",
"supply chain analyst",
"supply planner",
"demand planner",
"procurement specialist",
"procurement engineer",
"purchasing manager",
"buyer",
"strategic sourcing",
"logistics manager",
"logistics executive",
"warehouse manager",
"inventory controller"

],

# ==========================================================
# RETAIL
# ==========================================================

"RETAIL":[

"store manager",
"retail manager",
"retail executive",
"merchandiser",
"visual merchandiser",
"cashier",
"floor manager",
"retail associate"

],

# ==========================================================
# HOSPITALITY
# ==========================================================

"HOSPITALITY":[

"hotel manager",
"restaurant manager",
"chef",
"sous chef",
"executive chef",
"cook",
"bartender",
"front office executive",
"guest relations",
"housekeeping manager",
"travel consultant",
"tour manager"

],

# ==========================================================
# TELECOM
# ==========================================================

"TELECOM":[

"telecom engineer",
"rf engineer",
"radio engineer",
"network planner",
"5g engineer",
"lte engineer",
"telecommunications engineer"

],

# ==========================================================
# GIS
# ==========================================================

"GIS":[

"gis analyst",
"gis engineer",
"geospatial engineer",
"remote sensing",
"cartographer",
"survey engineer"

],

# ==========================================================
# ARCHITECTURE
# ==========================================================

"ARCHITECTURE":[

"architect",
"solution architect",
"enterprise architect",
"technical architect",
"cloud architect",
"application architect",
"interior designer",
"interior architect"

],

# ==========================================================
# MEDIA
# ==========================================================

"MEDIA":[

"video editor",
"motion graphics designer",
"animator",
"2d animator",
"3d animator",
"vfx artist",
"photographer",
"cinematographer",
"journalist",
"news reporter",
"anchor"

],

# ==========================================================
# SCIENCE
# ==========================================================

"SCIENCE":[

"chemist",
"physicist",
"mathematician",
"statistician",
"research fellow",
"scientific officer",
"scientist",
"laboratory scientist"

]
}
# ============================================================
# TEXT CLEANING
# ============================================================


def clean_text(text: str) -> str:
    """Normalize headline for matching."""
    if text is None:
        return ""

    text = str(text).lower()
    text = text.replace("&", " and ")
    text = text.replace("/", " ")
    text = text.replace("-", " ")
    text = text.replace("_", " ")

    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# FUZZY MATCHING
# ============================================================


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def keyword_score(headline, keyword):
    """
    Score one keyword against one headline.
    """

    headline = clean_text(headline)
    keyword = clean_text(keyword)

    if keyword in headline:
        return 100

    if headline == keyword:
        return 100

    words = headline.split()

    for word in words:
        if similarity(word, keyword) > 0.92:
            return 85

    score = similarity(headline, keyword)

    if score > 0.90:
        return 90

    if score > 0.80:
        return 75

    return 0


# ============================================================
# CATEGORY DETECTION
# ============================================================


def detect_category(headline):

    headline = clean_text(headline)

    best_category = "OTHER"
    best_score = 0

    for category, keywords in ROLE_KEYWORDS.items():

        current_best = 0

        for keyword in keywords:

            score = keyword_score(headline, keyword)

            if score > current_best:
                current_best = score

        if current_best > best_score:
            best_score = current_best
            best_category = category

    return best_category, best_score


# ============================================================
# BONUS PRIORITY
# ============================================================

EXACT_PRIORITY = {
    "ai engineer": 120,
    "machine learning engineer": 120,
    "ml engineer": 119,
    "generative ai engineer": 118,
    "llm engineer": 118,
    "computer vision engineer": 117,
    "nlp engineer": 117,
    "deep learning engineer": 116,
    "prompt engineer": 116,
    "mlops engineer": 115,
    "data scientist": 120,
    "senior data scientist": 118,
    "lead data scientist": 117,
    "data analyst": 120,
    "business intelligence analyst": 119,
    "bi analyst": 118,
    "analytics engineer": 117,
    "business analyst": 120,
    "senior business analyst": 118,
    "data engineer": 120,
    "big data engineer": 119,
    "software engineer": 120,
    "software developer": 118,
    "application developer": 117,
    "backend engineer": 120,
    "backend developer": 119,
    "frontend engineer": 120,
    "frontend developer": 119,
    "full stack developer": 120,
    "full stack engineer": 119,
    "devops engineer": 120,
    "cloud engineer": 119,
    "qa engineer": 120,
    "test engineer": 118,
    "android developer": 120,
    "ios developer": 120,
    "product manager": 120,
    "ui designer": 120,
    "ux designer": 120,
}


def priority_score(headline):

    headline = clean_text(headline)

    if headline in EXACT_PRIORITY:
        return EXACT_PRIORITY[headline]

    best = 0

    for key, value in EXACT_PRIORITY.items():

        if key in headline:
            best = max(best, value)

    return best


# ============================================================
# HEADLINE EXTRACTOR
# ============================================================
def get_headline(candidate):

    profile = candidate.get("profile", {})

    headline = (
        profile.get("headline")
        or profile.get("current_title")
        or candidate.get("headline")
        or candidate.get("title")
        or ""
    )

    # Keep only the primary job title before '|'
    headline = headline.split("|")[0].strip()

    return headline

# ============================================================
# SORT KEY
# ============================================================


def candidate_sort_key(candidate):

    headline = get_headline(candidate)

    category, score = detect_category(headline)

    priority = CATEGORY_PRIORITY.get(category, 999)

    bonus = priority_score(headline)

    return (priority, -bonus, -score, clean_text(headline))


# ============================================================
# CATEGORY COUNTER
# ============================================================

category_counter = defaultdict(int)
# ============================================================
# JSONL READER
# ============================================================


def read_jsonl(file_path):

    candidates = []

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"{file_path} not found.")

    print(f"\nReading {file_path.name}...\n")

    with open(file_path, "r", encoding="utf-8") as f:

        for line in tqdm(f, desc="Loading Candidates"):

            line = line.strip()

            if not line:
                continue

            try:

                obj = json.loads(line)
                candidates.append(obj)

            except json.JSONDecodeError:
                continue

    print(f"\nLoaded {len(candidates):,} candidates.\n")

    return candidates


# ============================================================
# ASSIGN CATEGORY
# ============================================================


def assign_categories(candidates):

    print("Detecting job categories...\n")

    for candidate in tqdm(candidates):

        headline = get_headline(candidate)

        category, score = detect_category(headline)

        candidate["_category"] = category
        candidate["_match_score"] = score
        candidate["_priority_score"] = priority_score(headline)

        category_counter[category] += 1

    return candidates


# ============================================================
# SORT
# ============================================================


def sort_candidates(candidates):

    print("\nSorting candidates...\n")

    candidates.sort(key=candidate_sort_key)

    return candidates


# ============================================================
# CATEGORY SUMMARY
# ============================================================


def print_summary():

    print("\n")
    print("=" * 60)
    print("CATEGORY SUMMARY")
    print("=" * 60)

    total = sum(category_counter.values())

    for category in sorted(
        category_counter.keys(), key=lambda x: CATEGORY_PRIORITY.get(x, 999)
    ):

        count = category_counter[category]

        percentage = (count / total) * 100 if total else 0

        print(f"{category:20} " f"{count:6d} " f"({percentage:5.2f}%)")

    print("=" * 60)
    print(f"TOTAL : {total:,}")
    print("=" * 60)


# ============================================================
# WRITE OUTPUT
# ============================================================
def write_jsonl(candidates, output_file):

    print(f"\nWriting {output_file}...\n")

    with open(output_file, "w", encoding="utf-8") as f:

        for candidate in tqdm(candidates, desc="Writing"):

            candidate.pop("_category", None)
            candidate.pop("_match_score", None)
            candidate.pop("_priority_score", None)

            json.dump(candidate, f, ensure_ascii=False)

            f.write("\n")


# ============================================================
# MAIN
# ============================================================


def main():

    candidates = read_jsonl(INPUT_FILE)

    candidates = assign_categories(candidates)

    candidates = sort_candidates(candidates)

    print_summary()

    write_jsonl(candidates, OUTPUT_FILE)

    print("\n")
    print("=" * 60)
    print("DONE!")
    print("=" * 60)
    print(f"Input File : {INPUT_FILE}")
    print(f"Output File: {OUTPUT_FILE}")
    print("=" * 60)


if __name__ == "__main__":

    main()
