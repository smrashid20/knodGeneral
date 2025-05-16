import sys

import transformers
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import os
from tqdm import tqdm


os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"

model_id = "meta-llama/Meta-Llama-3.1-70B-Instruct"

# =======================
MAX_NEW_TOKENS = 8000
# TEMPERATURE = 0.6
TEMPERATURE = 0.2
TOP_P = 0.9
# MAX_LENGTH = 2500
# TOP_K = 10
# NUM_RETURNED_SEQUENCES = 1

# =======================

access_token = "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"
print("Access token :", access_token)

# quantization_config = BitsAndBytesConfig(load_in_8bit=False)


model = AutoModelForCausalLM.from_pretrained(model_id, token=access_token,
    device_map="auto",
    torch_dtype="auto",
    load_in_8bit=False)
print("Model loaded")


tokenizer = AutoTokenizer.from_pretrained(model_id, token=access_token)
print("Tokenizer loaded")


pipeline = transformers.pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    torch_dtype="auto",
    trust_remote_code=True,
    device_map="auto",
    token=access_token,
    # max_length=MAX_LENGTH,
    # truncation=True
)
print("Pipeline loaded")

# llama-3
terminators = [
    pipeline.tokenizer.eos_token_id,
    pipeline.tokenizer.convert_tokens_to_ids("<|eot_id|>")
]

def generate_repair_description_llama(repair_prompt, output_file):

    messages = [
        {"role": "system", "content": "You are an helpful AI assistant."
                                      "You will generate repair steps for the code patch provided."
                                      "The text should be within 500 words."},
        {"role": "user", "content": repair_prompt},
    ]

    # llama-3
    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    # print("prompt: \n===========\n\n", prompt)
    # print("======================================================")

    output_sequences = pipeline(
        prompt,
        max_new_tokens=MAX_NEW_TOKENS,
        eos_token_id=terminators,
        do_sample=True,
        temperature=TEMPERATURE,
        top_p=TOP_P,
    )

    # llama-3
    output = output_sequences[0]["generated_text"][len(prompt):]
    # output = str(output_sequences)

    # write to output file
    with open(output_file, 'w') as f:
        f.write(output)


def summarize_with_llama(text):

    prompt = "Summarize the following text within 250 words:\n\n" + text

    messages = [
        {"role": "system", "content": "You are an helpful AI assistant."
                                      "You will summarize the text provided."
                                      "The text should be within 250 words."},
        {"role": "user", "content": prompt},
    ]

    # llama-3
    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    # print("prompt: \n===========\n\n", prompt)
    # print("======================================================")

    output_sequences = pipeline(
        prompt,
        max_new_tokens=MAX_NEW_TOKENS,
        eos_token_id=terminators,
        do_sample=True,
        temperature=TEMPERATURE,
        top_p=TOP_P,
    )

    # llama-3
    output = output_sequences[0]["generated_text"][len(prompt):]
    # output = str(output_sequences)

    return output


def generate_gt_reasoning_llama(vulnerability_description, buggy_block, fixed_block, output_file):

    prompt = ("Explain the reasoning, in natural language text, for the following repair to fix the vulnerability within 500 words.\n "
              "Do not use any code in your reasoning.\n"
              "Here is the vulnerability description:\n<vulnerability_description>\n" + vulnerability_description + "</vulnerability_description>\n"
              "Here is the buggy code.\n" + "<buggy_code>\n" + buggy_block + "\n</buggy_code>\nHere is the repair:\n" +
              "<repair_code>\n" + fixed_block + "\n</repair_code>\n")

    messages = [
        {"role": "system", "content": "You are an helpful AI assistant."
                                      "You will generate a natural language text reasoning for a given fix for a vulnerability. Do not use any code in your reasoning."
                                      "The text should be within 500 words."},
        {"role": "user", "content": prompt},
    ]

    # llama-3
    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    # print("prompt: \n===========\n\n", prompt)
    # print("======================================================")

    output_sequences = pipeline(
        prompt,
        max_new_tokens=MAX_NEW_TOKENS,
        eos_token_id=terminators,
        do_sample=True,
        temperature=TEMPERATURE,
        top_p=TOP_P,
    )

    # llama-3
    output = output_sequences[0]["generated_text"][len(prompt):]
    # output = str(output_sequences)

    # write to output file
    with open(output_file, 'w') as f:
        f.write(output)


def generate_patch_reasoning_llama(buggy_block, fixed_block, output_file):

    prompt = ("In 500 words, explain the steps taken in a proposed patch, in natural language text. The patch tries to fix a vulnerability.\n "
              "Do not use any code in your reasoning.\n"
              "Here is the buggy code.\n" + "<buggy_code>\n" + buggy_block + "\n</buggy_code>\nHere is the proposed patch:\n" +
              "<proposed_patch>\n" + fixed_block + "\n</proposed_patch>\n")

    messages = [
        {"role": "system", "content": "You are an helpful AI assistant."
                                      "You will generate a natural language that explains the steps taken in a proposed patch. Do not use any code in your reasoning."
                                      "The text should be within 500 words."},
        {"role": "user", "content": prompt},
    ]

    # llama-3
    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    # print("prompt: \n===========\n\n", prompt)
    # print("======================================================")

    output_sequences = pipeline(
        prompt,
        max_new_tokens=MAX_NEW_TOKENS,
        eos_token_id=terminators,
        do_sample=True,
        temperature=TEMPERATURE,
        top_p=TOP_P,
    )

    # llama-3
    output = output_sequences[0]["generated_text"][len(prompt):]
    # output = str(output_sequences)

    # write to output file
    with open(output_file, 'w') as f:
        f.write(output)



def evaluate_reasoning_llama(gt_reasoning, eval_reasoning):

    prompt = ("Assess whether the two provided reasoning for repair are same or not. Output YES if they are the similar or NO if not in the first line.\n"
              "Ground Truth Reasoning:\n<gt_reasoning>\n" + gt_reasoning + "\n</gt_reasoning>\n"
              "Here is the reasoning provided:\n<provided_reasoning>\n" + eval_reasoning + "\n</provided_reasoning>\n")

    messages = [
        {"role": "system", "content": "You are an helpful AI assistant."
                                      "You will evaluate two text reasoning of vulnerability fixes and decide whether they are similar or not. You will only output YES or NO in the"
                                      "first line."
                                      "YES if they agree and NO if they do not."},
        {"role": "user", "content": prompt},
    ]

    # llama-3
    prompt = pipeline.tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    # print("prompt: \n===========\n\n", prompt)
    # print("======================================================")

    output_sequences = pipeline(
        prompt,
        max_new_tokens=MAX_NEW_TOKENS,
        eos_token_id=terminators,
        do_sample=True,
        temperature=TEMPERATURE,
        top_p=TOP_P,
    )

    # llama-3
    output = output_sequences[0]["generated_text"][len(prompt):]

    # if YES is in first line of output, return true, otherwise false
    if "YES" in output.split("\n")[0].strip():
        return True
    else:
        return False