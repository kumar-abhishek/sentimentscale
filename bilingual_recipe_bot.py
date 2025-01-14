import streamlit as st

import pandas as pd
import re
import random
from datetime import datetime

## have to set random seed, otherwise the text_input elements will be a mess on if-else conditions

#seed_no = random.randint(0,9) ## cannot be a random number everytime the page reloads
# better fix it for a certain time duration e.g. a day/ a particular hour
seed_no = datetime.now().hour

random.seed(seed_no)

@st.cache
def load_data(recipe_path):
     return pd.read_csv(recipe_path).dropna()

def recipe_bot_query(liked_ingredients):
    
    #initialize a new df
    filtered = recipe_db
    for i,ing in enumerate(liked_ingredients):
        mask= filtered['ingredients'].str.contains(ing)
        filtered = filtered[mask]
    
    return filtered

def recipe_remove(matching_recipes_df,disliked_ingredients):
    filtered = matching_recipes_df
    for i,ing in enumerate(disliked_ingredients):
        masked= filtered['ingredients'].str.contains(ing)
        filtered = filtered.mask(masked).dropna()
    
    return filtered

def rank_recipe(cleaned_recipes,sort_order):
    
    if  'random' in sort_order: #random order
        cleaned_recipes = cleaned_recipes.sample(frac=1)
    elif 'recent' in sort_order: #sort by recency
        cleaned_recipes = cleaned_recipes.sort_values("submitted",ascending = False)
    
    return cleaned_recipes

def rank_recipe_ch(cleaned_recipes,sort_order):
    
    if  sort_order in ["要","好","哦"]: #random order
        cleaned_recipes = cleaned_recipes.sample(frac=1)
    
    return cleaned_recipes

def next_one(try_or_not):
    if try_or_not in ["yes","y","sure","alright","ok","okay","why not"] or "yes" in try_or_not:
        sent1 = "These are the steps of making this cuisine:"
        recipe_row = sorted_recipes.iloc[0]
    else:
        recipe_row = sorted_recipes.iloc[1]
        sent1 = "This is another recipe: " +f"`{recipe_row['name'].capitalize()}`" + "  \n  \n" + "Ingredients in this recipe: " + ", ".join(eval(recipe_row['ingredients'])) + "  \n  \n" + "Steps of this recipe:"
    yield sent1
        
    
    for step in eval(recipe_row['steps']): #turn str back into a list
        step_str = "> "+step 
        yield step_str

def next_one_ch(try_or_not):
    if try_or_not in ["要","好","哦","試","試吓","OK","ok","okay"] or "好" in try_or_not:
        sent1 = "烹調步驟如下:"
        recipe_row = sorted_recipes.iloc[0]
    else:
        # add a random pick here
        recipe_len = len(sorted_recipes)
        randint = random.randint(0,recipe_len)
        recipe_row = sorted_recipes.iloc[randint]
        sent1 = "試吓下一個食譜: " +f"`{recipe_row['title']}`" + "  \n  \n 會用到的食材：" + " " + ", ".join(eval(recipe_row['ingredients'])) + "  \n  \n" + "烹調步驟如下:"
    yield sent1
        
    
    for step in eval(recipe_row['steps']): #turn str back into a list
        step_str = "> "+step 
        yield step_str
    
## predefined template for QA
### text_input element ids are uniquely defined by their label(a string). liked_ingredients(variable assigned to user-input value of text_input) will disappear if page refresh to another text_input element with a different label.

#English version       
Q1_candidates = ["Any ingredient(s) you want to taste in the meal?",
                    "Any food you have in mind to start search?",
                    "Tell me food(s) you like.",
                    "What ingredients do you like?"]
Q1 = random.choice(Q1_candidates)

Q2_candidates = ["Is there any ingredient(s) you hate? I can filter them out.",
                    "What ingredient(s) would you like to avoid?",
                    "Is there something you don't eat?",
                    "There's plenty of choices! You can narrow down further by removing recipes containing certain ingredients. What would you like to filter?"]
Q2 = random.choice(Q2_candidates)


## get varied replies
def get_R1(matching_recipes_df, liked_ingredients):
    R1_candidates = [f"Okay! {len(matching_recipes_df)} recipes match your choice.", 
                f"I can find {len(matching_recipes_df)} recipes in the database that contain {' and '.join(liked_ingredients)}.",
                f"Alright! There are {len(matching_recipes_df)} recipes available for your selection. "]

    R1 = random.choice(R1_candidates)
    return R1 


def get_R2(cleaned_recipes,disliked_ingredients):
    R2_candidates = [f"I see. After filtering out those ingredients, {len(cleaned_recipes)} recipes remain.",
                f"Sure I can remove recipes containing {' and '.join(disliked_ingredients)}! You have narrowed down the number of recipes to {len(cleaned_recipes)}. ",
                f"I don't like {','.join(disliked_ingredients)} too! Now we have  {len(cleaned_recipes)} options left."]
    R2 = random.choice(R2_candidates)
    return R2 

#Chinese version 
Q1_candidates_ch = ["話我知一種或幾種你想食嘅餸？",
                    "有咩想食？",
                    "你鍾意食咩？",
                    "有咩食材想試吓？"]
Q1_ch = random.choice(Q1_candidates_ch)

Q2_candidates_ch = ["有咩唔食？我可以篩走。",
                    "有無嘢你唔食?",
                    "話我知一種或幾種你唔鍾意食嘅食物?",
                    "有咩食物你想避開？"]
Q2_ch = random.choice(Q2_candidates_ch)


## get varied replies
def get_R1_ch(matching_recipes_df, liked_ingredients):
    R1_candidates = [f"得! {len(matching_recipes_df)}個食譜符合你嘅要求。", 
                f"我搵到{len(matching_recipes_df)}個食譜係包括 {' 同 '.join(liked_ingredients)}。",
                f"OK! 合共有{len(matching_recipes_df)}個食譜俾你揀。 "]

    R1 = random.choice(R1_candidates)
    return R1 


def get_R2_ch(cleaned_recipes,disliked_ingredients):
    R2_candidates = [f"哦～篩完仲有{len(cleaned_recipes)}個食譜。",
                f"無問題！我可以篩走含有{' 同埋 '.join(disliked_ingredients)}的食譜! 而家剩低 {len(cleaned_recipes)}個食譜。 ",
                f"我都唔鍾意食{'同埋'.join(disliked_ingredients)}啊。而家仲有 {len(cleaned_recipes)}個選擇。"]
    R2 = random.choice(R2_candidates)
    return R2



## start streamlit interface
lang_selected = st.sidebar.selectbox("Language",["English","廣東話"])

if lang_selected == "廣東話":
    recipe_path = r"chinese_recipes_3cols.csv"
    recipe_db = load_data(recipe_path)

    st.header("問吓搵食譜小助手: 今餐食乜餸？")
    st.text("食譜源於史雲生和煤氣烹飪中心，版權歸屬原作者所有。")

    liked_ingredients = st.text_input(Q1_ch,"")
    #st.write(liked_ingredients)

    if liked_ingredients:
        
        liked_ingredients = re.split('[ ,;//、， ]',liked_ingredients.lower().strip(" !?.！？。"))
        matching_recipes_df = recipe_bot_query(liked_ingredients)
        
        R1 = get_R1_ch(matching_recipes_df,liked_ingredients)
        st.write(R1)

        disliked_ingredients = st.text_input(Q2_ch,"")
        #st.write(disliked_ingredients)

        if disliked_ingredients:
            disliked_ingredients = [t for t in re.split('[ ,;//、， ]',disliked_ingredients.lower().strip(" !?.！？。")) if t != ""]
            
            cleaned_recipes = recipe_remove(matching_recipes_df,disliked_ingredients)

            
            st.write(get_R2_ch(cleaned_recipes,disliked_ingredients))

            #sort_order = st.text_input("你要隨機揀一個食譜嗎？","")
            #if sort_order:

            #    sorted_recipes = rank_recipe_ch(cleaned_recipes, sort_order)
            
            sorted_recipes = cleaned_recipes
            #st.write(sorted_recipes['title'])
            
            
            recipe_option = st.selectbox("你可以揀一個食譜試試～",sorted_recipes['title'].values)
            selected_option = sorted_recipes.query('title == @recipe_option').iloc[0]
            st.write( "`"+selected_option['title']+ "`")
            st.write( ", ".join(eval(selected_option['ingredients'])))
            for step in eval(selected_option['steps']): #turn str back into a list
                step_str = "> "+step 
                st.write(step_str)

            # st.write(f"符合條件的其中一個食譜: " + "`"+sorted_recipes['title'].iloc[0]+"`")
            # st.write("呢個食譜會用到以下材料: " +", ".join(eval(sorted_recipes['ingredients'].iloc[0])))

            # try_or_not =  st.text_input("要唔要試吓？","")
            # if try_or_not:
            #     for return_str in next_one_ch(try_or_not):
            #         st.markdown(return_str)

else:
    recipe_path = "recipes_4cols.csv"
    recipe_db = load_data(recipe_path)

    st.header("Ask chatbot: What should I cook now?")
    st.text("Recipes originated from user-uploaded content on Food.com")

    liked_ingredients = st.text_input(Q1,"")
    #st.write(liked_ingredients)

    if liked_ingredients:
        
        liked_ingredients = re.split('[ ,;//]',liked_ingredients.lower().strip(" !?."))
        matching_recipes_df = recipe_bot_query(liked_ingredients)
        
        R1 = get_R1(matching_recipes_df,liked_ingredients)
        st.write(R1)

        disliked_ingredients = st.text_input(Q2,"")
        #st.write(disliked_ingredients)

        if disliked_ingredients:
            disliked_ingredients = [t for t in re.split('[ ,;//]',disliked_ingredients.lower().strip(" !?.")) if t != ""]
            
            cleaned_recipes = recipe_remove(matching_recipes_df,disliked_ingredients)

            
            st.write(get_R2(cleaned_recipes,disliked_ingredients))

            sort_order = st.text_input("Do you want the first one, a random recipe or the most recent recipe?","")
            if sort_order:

                sorted_recipes = rank_recipe(cleaned_recipes, sort_order.lower())
        
                st.write(f"Here is the recipe: " + "`"+sorted_recipes['name'].iloc[0].capitalize()+"`")
                st.write("Ingredients in this recipe: " +", ".join(eval(sorted_recipes['ingredients'].iloc[0])))

                try_or_not =  st.text_input("Do you want to try it?","").lower()
                if try_or_not:
                    for return_str in next_one(try_or_not):
                        st.markdown(return_str)
