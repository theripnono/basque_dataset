import time,re,csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from wikihow import create_dataset,count_word

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def main():

    rws=int(input(f"How many rows you want to create?: "))
    if type(rws) is int:
        dataset = create_dataset(rows=rws)

    def check_modal_error():

        error_modal_xpath = "//*[@class='modal-dialog modal-sm modal-notify modal-danger']"
        try:
            error_modal = driver.find_element(By.XPATH, error_modal_xpath)
            if error_modal.is_displayed():
                print("Error modal detected. Handling...")
                button_xpath = "//*[@id='centralModalDanger']/div/div/div[1]/button"
                driver.find_element(By.XPATH, button_xpath).click()

                button = driver.find_element(By.XPATH,"//*[@id='translate_text']/div[1]/div[1]/div/div[3]/div[3]/div[2]/button")
                button.click()

                return True  # Error modal detected
        except:
            return False  # No error modal detected

    def chunk_text(text:str, max_words=50)->list:

        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
        chunks = []
        current_chunk = []

        for sentence in sentences:
            words = sentence.split()
            current_chunk.extend(words)

            if len(current_chunk) >= max_words:
                chunks.append(current_chunk)
                current_chunk = []

        if current_chunk:
            chunks.append(current_chunk)

        return chunks

    def restart():

        global tries
        # restart browser:
        driver.close()

        tries=0

        url = "https://elia.eus/traductor"
        driver.get(url)
        time.sleep(2)

        button = driver.find_element(By.XPATH, "//a[@class='btn btn-elhuyar btn-block mb-2 accept_cookies waves-effect waves-light']")
        button.click()

        return tries


    def to_translate(text_list,row,flag):
        if flag=='galdera':
            row['galdera']=''
        if flag=='erantzuna':
            row['erantzuna']=''
        if flag=='pausoak':
            row['pausoak']=''

        wait = 1
        tries = 0

        for text in text_list:
            joined_sentence = ' '.join(text)
            input_box = driver.find_element(By.XPATH, "//*[@id='input_text']")
            input_box.send_keys(joined_sentence)
            time.sleep(2)
            button = driver.find_element(By.XPATH,"//*[@id='translate_text']/div[1]/div[1]/div/div[3]/div[3]/div[2]/button")
            button.click()
            output_text = driver.find_element(By.XPATH, "//*[@id='output_text_dummy']")
            out_text = output_text.text

            #Wait until the text is translated
            while len(out_text)==0:
                time.sleep(2)
                print("Translating:","#"*(wait+1))
                output_text = driver.find_element(By.XPATH, "//*[@id='output_text_dummy']")
                out_text = output_text.text

                wait+=1
                if check_modal_error():
                    tries+=1
                    if tries>=20:
                        print("Many modal error has been detected... The program will be closed")
                        driver.close
                        export_to_csv(dataset)
                        print("The dataset was forced to be exported")
                    continue

                if len(out_text) !=0:
                    print("*** Translation Done! ***")
                    wait = 1
                    break

            if flag=='galdera':
                row['galdera'] += out_text
            if flag=='erantzuna':
                row['erantzuna'] += out_text
            if flag=='pausoak':
                row['pausoak'] += out_text


            #Delete text
            delete_text = driver.find_element(By.XPATH, "//*[@id='delete_text_source']")
            time.sleep(2)
            delete_text.click()
            time.sleep(2)

        return row

    def export_to_csv(dataset):
        today_date = time.strftime('%Y_%m_%d')
        csv_file_path = f"{today_date}_output_dataset.csv"
        field_names = dataset[0].keys()

        # Write the dataset to the CSV file
        with open(csv_file_path, mode='w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=field_names)

            # Write the header
            writer.writeheader()

            # Write the rows
            writer.writerows(dataset)

        print(f"Dataset exported to {csv_file_path}")

    url = "https://elia.eus/traductor"
    driver.get(url)

    time.sleep(2)

    button = driver.find_element(By.XPATH, "//a[@class='btn btn-elhuyar btn-block mb-2 accept_cookies waves-effect waves-light']")
    button.click()

    count_row = 1

    for row in dataset:
        print(f"Title: {row['title']}")

        galdera = row['title']
        erantzuna = row['intro']
        pausoak = row['methods']

        galdera = chunk_text(galdera) # list
        erantzuna = chunk_text(erantzuna)  # list
        pausoak = chunk_text(pausoak)  # list

        galdera_lerroa = to_translate(galdera,row,flag='galdera')
        row['galdera_len']=count_word(galdera_lerroa['galdera'])

        erantzuna_lerroa = to_translate(erantzuna,row,flag="erantzuna")
        row['erantzuna_len']=count_word(erantzuna_lerroa['erantzuna'])
        pausoak_lerroa = to_translate(pausoak,row,flag='pausoak')
        row['pausoak_len']=count_word(pausoak_lerroa['pausoak'])

        print(f"Row: {count_row} is successfully updated!")
        count_row+=1
    # close browser
    driver.close()

    # Export dataset to CSV
    export_to_csv(dataset)
    print("The dataset was successfully translated!")

if __name__=='__main__':
    main()