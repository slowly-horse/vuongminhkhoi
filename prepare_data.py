from prompt import Prompter
# import datasets
# from transformers import AutoTokenizer
from datasets import load_dataset

# def create_datasets(tokenizer: AutoTokenizer, data_path: str, max_length: int, seed: int, size_valid_set: int, split: str):
#     def convert_conversation_to_input(examples):
#         input_ids = [tokenizer.apply_chat_template(conversation, tokenize=True)[: max_length] for conversation in examples['conversations']]
#         return {'input_ids': input_ids}
        
#     dataset = datasets.load_dataset(data_path, split=split)
#     dataset = dataset.map(convert_conversation_to_input, remove_columns=list(dataset.features), batched=True)
    
#     dataset = dataset.train_test_split(test_size=size_valid_set, shuffle=True, seed=seed)

#     train_data = dataset['train'].shuffle()
#     valid_data = dataset['test']

#     return train_data, valid_data

def create_datasets(data_path, size_valid_set, tokenizer, max_length, seed):
    def tokenize(prompt, add_eos_token=True):
        result = tokenizer(
            prompt,
            truncation=True,
            max_length=max_length,
            padding=False,
            return_tensors=None
            )

        if (
            result["input_ids"][-1] != tokenizer.eos_token_id
            and len(result["input_ids"]) < max_length
            and add_eos_token
        ):
            
            result["input_ids"].append(tokenizer.eos_token_id)
            result["attention_mask"].append(1)

        result["labels"] = result["input_ids"].copy()
        return result

    
    def generate_and_tokenize_prompt(data_point):
        full_prompt = prompter.generate_prompt(
            data_point["instruction"],
            data_point["input"],
            data_point["output"],
        )
        tokenized_full_prompt = tokenize(full_prompt)

        return tokenized_full_prompt
    
    prompter = Prompter()

    print(f"Load dataset....")
    dataset = load_dataset('json', split='train', data_files=data_path)
    dataset = dataset.train_test_split(test_size=size_valid_set, seed=seed)

    train_data = dataset["train"].shuffle().map(generate_and_tokenize_prompt)
    valid_data = dataset["test"].map(generate_and_tokenize_prompt)
    
    train_data.set_format("torch")
    valid_data.set_format("torch")
    
    train_data = train_data.remove_columns(['instruction', 'input', 'output'])
    valid_data = valid_data.remove_columns(['instruction', 'input', 'output'])

    dataset["test"].to_json('dataset/val_data.json')
    
    return train_data, valid_data
