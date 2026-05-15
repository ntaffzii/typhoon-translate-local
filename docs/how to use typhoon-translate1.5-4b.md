Typhoon Translate 1.5

Typhoon-Translate v1.5 is a lightweight, 4-billion-parameter language model designed specifically for controllable, high-quality Thai ↔ English translation—right from your local device.

Building on feedback from Typhoon-Translate v1, version 1.5 addresses the controllability issues of the previous release. It introduces promptable translation rules and supports flexible translation instructions for more accurate and customizable results.

Release Blog available on OpenTyphoon Blog

Performance
We used GPT-4o-mini as an "AI judge", comparing Typhoon Translate against its own generations and other top systems.

Model Description
Model type: A 4B instruct decoder-only model based on Qwen3 architecture.
Requirement: transformers 4.51.1 or newer.
Primary Language(s): Thai 🇹🇭 and English 🇬🇧
License: Gemma License
Quickstart
This code snippet shows how to use the Typhoon translation model for Thai or English text generation using the transformers library with a specific prompt.

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

model_id = "scb10x/typhoon-translate1.5-4b"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)

# Translate English to Thai
messages = [
     {"role": "user", "content": "Translate the following English text into Thai, strictly following the rules below and return only the translated text.\nRules:\n1.  Translate "Immigration Bureau" as "สำนักงานตรวจคนเข้าเมือง".\n2.  Translate "Permanent Residence Permit" as "ใบอนุญาตถิ่นที่อยู่ถาวร".\n3.  Translate "Department of Employment" as "กรมการจัดหางาน".\n4.  Translate "Immigration Act B.E. 2522" as "พระราชบัญญัติตรวจคนเข้าเมือง พ.ศ. 2522".\n5.  Translate "appeal petition" as "คำร้องอุทธรณ์".\n6.  Translate "supporting documentation" as "เอกสารประกอบการพิจารณา".\n7.  Translate "Office of Legal Affairs" as "กองกฎหมาย".\n8.  Do not translate or alter any personally identifiable information (PII) such as names, addresses, dates, or reference numbers.\n9.  The translation must use a highly formal, official tone (ภาษาทางการ/ราชการ) appropriate for a government document.\nSource Text:\n[Official Letterhead]\nKingdom of Thailand\nMinistry of the Interior\nImmigration Bureau\nCase File Number: 88-1-2567-00432\nDate: September 26, 2024\nTo:\nMr. Johnathan Alistair Smith\n123/45 Sukhumvit Soi 55 (Thong Lo)\nKhlong Tan Nuea, Watthana\nBangkok 10110, Thailand\nSubject: Official Notification Regarding Your Residency Status (Permanent Residence Permit No. PR-2018-98765)\nDear Mr. Smith,\nThis letter serves as an official notification from the Immigration Bureau to inform you that we have initiated proceedings to review and potentially revoke your Permanent Residence Permit (No. PR-2018-98765), issued on January 12, 2018.\nOur records indicate that your application for a Permanent Residence Permit, submitted on October 15, 2017, was granted based on your continuous employment as a Senior Financial Analyst with the company 'Global Synergy Corp. (Thailand)', under the condition that you maintain lawful employment status within the Kingdom.\nHowever, pursuant to an investigation conducted in collaboration with the Department of Employment, it has come to our attention that your employment with said company was formally terminated on March 1, 2024. You failed to report this critical change in your employment status to the Immigration Bureau within the legally mandated 90-day period, a direct violation of Section 37(5) of the **Immigration Act B.E. 2522**, which states that the holder of such a permit must notify an immigration officer of any change in status that affects the original conditions of the permit.\nYou have the right to appeal this preliminary decision. You must submit a formal appeal petition to the Office of Legal Affairs at the Immigration Bureau headquarters, located at Government Complex Chaeng Watthana, Building B. The petition must be submitted in person, along with any supporting documentation that may justify your failure to report, no later than 4:30 PM on October 31, 2024.\nFailure to submit an appeal within the specified timeframe will result in the automatic and final revocation of your Permanent Residence Permit. Following such a decision, you will be required to leave the Kingdom of Thailand within seven (7) days.\nSincerely,\nPol. Maj. Gen. Suchart Vongvichai\nDeputy Commissioner\nImmigration Bureau"},
]

input_ids = tokenizer.apply_chat_template(
    messages,
    add_generation_prompt=True,
    return_tensors="pt",
).to(model.device)

outputs = model.generate(
    input_ids,
    max_new_tokens=8192,
    temperature=0.2,
)
response = outputs[0][input_ids.shape[-1]:]
print(tokenizer.decode(response, skip_special_tokens=True))

Prompting
Please use Translate the following {English/Thai} text into {Thai/English}, strictly following the rules below and return only the translated text. as below.

Translate the following {English/Thai} text into {Thai/English}, strictly following the rules below and return only the translated text.
{rules of translation}
Source Text:

{text_to_translate}

example of

Translate the following text into Thai.\n\nA banished celestial, Serai, cursed to walk as a mortal boy, fights against the Empire that slaughtered the skyborn.\nHe trains with humans, bonds with them, bleeds beside them. In secret, he regrows his wings through combat—but each feather only returns when he loses someone he loves.\nAt the climax, he ascends—glorious, radiant, unstoppable—only to find his friends gone, their memories etched into his wings.\nAs he watches the sun rise, his halo returns.\nHe whispers, “Was it worth it?”\nAnd no one answers.

Deploy as Server
This section shows how to run Typhoon translate as an OpenAI-compatible API server using vllm.

SGLang:
python3 -m sglang.launch_server scb10x/typhoon-translate1.5-4b --context-length 16000 --dtype bfloat16

vLLM:
vllm serve scb10x/typhoon-translate1.5-4b --max-model-len 16000 --dtype bfloat16

Best Practices
To achieve optimal performance, we recommend the following settings:

Use user prompt Translate the following {English/Thai} text into {Thai/English}, strictly following the rules below and return only the translated text.
Set low temperature.
Using an context length less than 8192 tokens.
Intended Uses & Limitations
This is a task-specific model intended to be used only with the provided prompts. It does not include any guardrails. Due to the nature of large language models (LLMs), a certain level of hallucination may occur. We recommend that developers carefully assess these risks in the context of their specific use case.

Follow us
https://twitter.com/opentyphoon

Support
https://discord.gg/us5gAYmrxw

Citation
If you find Typhoon2 useful for your work, please cite it using:
@misc{typhoon2,
      title={Typhoon 2: A Family of Open Text and Multimodal Thai Large Language Models}, 
      author={Kunat Pipatanakul and Potsawee Manakul and Natapong Nitarach and Warit Sirichotedumrong and Surapon Nonesung and Teetouch Jaknamon and Parinthapat Pengpun and Pittawat Taveekitworachai and Adisai Na-Thalang and Sittipong Sripaisarnmongkol and Krisanapong Jirayoot and Kasima Tharnpipitchai},
      year={2024},
      eprint={2412.13702},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2412.13702}, 
}