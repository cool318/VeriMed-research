"""
Synthetic and real clinical text for demo/testing purposes only.
No real patient data is used anywhere in this project. The Spanish case
is real, published, de-identified clinical narrative — see README.
"""

SAMPLE_SOURCE = """
The patient is a 58-year-old male presenting with a two-week history of
worsening shortness of breath and lower limb swelling. He reports no
chest pain. His past medical history includes hypertension, diagnosed
five years ago, currently managed with lisinopril 10mg daily. He denies
any history of diabetes or prior cardiac events. On examination, blood
pressure was 148/92 mmHg, heart rate 96 bpm, and oxygen saturation 94
percent on room air. Bilateral pitting edema was noted to the mid-shin.
Chest auscultation revealed bibasilar crackles. An echocardiogram was
ordered to assess left ventricular function. The patient was started on
furosemide 40mg daily and advised to restrict sodium intake. Follow-up
was scheduled in two weeks to reassess symptoms and review echocardiogram
results.
"""

SAMPLE_SUMMARY_WITH_HALLUCINATION = """
This 58-year-old male has a two-week history of dyspnea and peripheral
edema. He has a history of hypertension and type 2 diabetes, managed
with lisinopril. He previously suffered a myocardial infarction two
years ago. Examination showed elevated blood pressure and reduced
oxygen saturation, with bilateral leg swelling and lung crackles. The
lisinopril dose was increased to 20mg daily. An echocardiogram was
ordered, and the patient was started on furosemide for fluid overload.
"""

NEURO_SOURCE = """
The patient is a 42-year-old female presenting with a three-day history
of progressively worsening headache, described as throbbing and located
over the left temple, with associated photophobia and nausea. She denies
any history of seizures, head trauma, or loss of consciousness. She
reports no family history of stroke or aneurysm. Past medical history is
notable for migraine with aura, diagnosed ten years ago, currently
managed with sumatriptan as needed. On examination, she was alert and
oriented, with normal cranial nerve function, normal strength and
sensation in all four limbs, and no papilledema on fundoscopy. Blood
pressure was 118/76 mmHg. A non-contrast CT head was ordered to exclude
secondary causes given the change in headache pattern. She was advised
to keep a headache diary and follow up in one week, with a plan to
consider MRI brain if symptoms persist or red flags develop.
"""

NEURO_SUMMARY_HALLUCINATED = """
This 42-year-old female presents with a three-day history of a
throbbing left temporal headache with photophobia and nausea. She has a
history of seizures and a family history of stroke. She has a ten-year
history of migraine with aura, managed with sumatriptan. Neurological
examination showed papilledema on fundoscopy. A CT head was ordered to
exclude secondary causes, and she was advised to follow up in one week.
"""

# Real clinical case — CodiEsp corpus, document S1889-836X2016000100006-1
# (CLEF eHealth 2020; Miranda-Escalada, Gonzalez-Agirre and Krallinger,
# 2020). CC-BY 4.0. Retrieved from the original open-access publication
# via SciELO. Text trimmed for length, not paraphrased or altered.
CODIESP_SOURCE_ES = """
Paciente varón de 65 años diagnosticado de OI a raíz de estudio de una
hija también afectada. No presentaba antecedentes familiares previos de
la enfermedad. Refería antecedente de varias fracturas, en número
aproximado de 6-7, durante la infancia y la adolescencia tras
traumatismos mínimos, la primera del húmero a los 2 años de edad.
Durante la edad adulta había tenido dos nuevas fracturas en codo y
hombro. Todas habían sido tratadas de forma conservadora. Recibió
tratamiento con calcio durante la infancia. Diagnosticado de
otoesclerosis, había sido intervenido quirúrgicamente para
estapedectomía de ambos oídos. Fue remitido a nuestra consulta por
osteoporosis detectada en densitometría ósea, que mostraba unas
T-scores de -3,4 en columna lumbar, -3 en cuello femoral y -2,8 en
fémur total. Se encontraba asintomático. En la exploración física
llamaba la atención una talla de 162 cm, escleras azules y presencia de
dentinogénesis imperfecta. No presentaba deformidades torácicas, ni en
columna dorsolumbar ni en miembros, salvo en codo derecho. Los niveles
de 25 hidroxivitamina D estaban en rango de insuficiencia, 22 ng/ml. Se
realizó estudio genético mediante secuenciación masiva de los genes
COL1A1, COL1A2, CRTAP y LEPRE1, detectándose en el gen COL1A1 una
deleción en heterocigosis de una Guanina. Se recomendó tratamiento con
alendronato semanal asociado a suplementos diarios de calcio y vitamina
D, evidenciándose una discreta mejoría densitométrica tras 1 año de
tratamiento.
"""

CODIESP_SUMMARY_HALLUCINATED_ES = """
Paciente varón de 65 años diagnosticado de osteogénesis imperfecta.
Presentaba antecedentes familiares previos de la enfermedad. Tuvo
varias fracturas durante la infancia tras traumatismos mínimos. Fue
remitido por osteoporosis detectada en densitometría ósea con T-scores
de -3,4 en columna lumbar. El estudio genético detectó una deleción en
el gen COL1A1. Se recomendó tratamiento con denosumab mensual. El
paciente también tiene diagnóstico de diabetes tipo 2.
"""
