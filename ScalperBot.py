from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from colorama import init, deinit, Fore, Back, Style

#colorama DOCS: https://pypi.org/project/colorama/

driverPATH = "E:\MAIN\Programming\Projects\Scalper\chromedriver.exe"    #path to chromedriver for selenium
#spreadSheetPATH = 'E:\MAIN\Programming\Projects\Scalper\GPUS.csv'   #path to CSV file that contains the GPU info
spreadSheetPATH = 'E:\MAIN\Programming\Projects\Scalper\Testing-ASUS.csv'  
checkoutPATH = 'E:\MAIN\Programming\Projects\Scalper\checkout.csv'
checkOutInfoDict = {} 
cashLimit = 1
tabDelay = 2
delay = .5

WebsiteInfo = {
	'BestBuy' : {'Color' : 'Blue', 'OOSText' : 'Sold Out', 'ISText' : 'Add to Cart', 'cartLink' : 'https://www.bestbuy.com/checkout/r/fulfillment', 'shippingButton':'Switch to Shipping', 'checkoutButtonText':'Checkout', 'ccInputID':'optimized-cc-card-number', 'expMonName':'expiration-month', 'expYearName':'expiration-year', 'ccSec':'credit-card-cvv','fNameInputID':'.firstName','lNameInputID':'.lastName','addrInputID':'.street','cityInputID':'.city','stateInputID':'.state','zipInputID':'.zipcode', 'emailInputID':'email', 'phoneInputID':'phone'},
    'Amazon' : {'Color' : 'Yellow', 'OOSText' : 'NULL', 'ISText' : 'NULL'},
	'NewEgg' : {'Color' : 'Orange', 'OOSText' : 'NULL', 'ISText' : 'NULL'},
    'ASUS' : {'Color' : 'Red', 'OOSText' : 'Arrival Notice', 'ISText' : 'Add to Cart', 'cartLink':'https://shop-us1.asus.com/AW000706/checkout', 'shippingButton':'Continue as Guest', 'fNameInputID':'customer-info-1__firstName'}
	}



'''
    Converts .csv spreadsheet file to list of dictionaries

        bool bPrint: True prints the list of dictionaries False does not print
'''
def getDict(path,bPrint):
    try:
        df = pd.read_csv(path)
    except:
        printError('Could not find csv file try changing the path')
        return None

    gpuDict = df.to_dict('records')
    if bPrint:
        print(gpuDict)
    
    return gpuDict


'''
    filter a list of dictionaries, returns a list of dictionaries containing features specified

        list dict: the list of dictionaries being passed in that gets filtered
        string filterKey: the key in the dictionary to filter by i.e. Brand, Model, Website, etc.
        string filterValue: the value to filter the dictionary by i.e. ASUS, GigaByte, MSI, etc.
        bool bFilt: if false don't filter the list if true then filter
'''
def filterDictionary(dictList, filterKey, filterValue, bFilt):
    #cum = list(filter(lambda x: x['Brand'] == 'ASUS', gpuDict))
    if not bFilt:
        return dictList
    return list(filter(lambda x: x[filterKey] == filterValue, dictList))

def printError(eMsg):
    print(Fore.RED + "ERROR: " + Fore.RESET + eMsg + Fore.RESET)


'''
    Opens a new tab in google chrome then saves the tab handle to the dictionary so it can be accessed later

    browser: The selenium driver
    dict gpuDict: A specific dictionary for GPU that gets updated with a WindowHandle key
'''
def newTab(browser, gpuDict):
    #if default tab then don't open new one
    browser.execute_script("window.open('" + gpuDict['URL'] + "');")
    windowHandle = browser.window_handles[-1]
    gpuDict['WindowHandle'] = windowHandle
    time.sleep(tabDelay)

def outOfStockPrint(gpu):
    print(gpu['Website'] + '_' + gpu['Model'] + " :" + Fore.RED + " OUT OF STOCK" + Fore.RESET)

def inStockPrint(gpu):
    print(gpu['Website'] + '_' + gpu['Model'] + " :" + Fore.GREEN + " IN STOCK" + Fore.RESET)

def waitForElementToLoad(browser, elemText):
    pageLoaded = False

    while not pageLoaded:
        try:
            browser.find_element_by_xpath("//*[contains(text(), '"+ elemText + "')]")
            print('pog')
            pageLoaded=True
        except:
            pageLoaded=False

def selectDropDown(dropdownBox, optionValue):
    dropdownBox.click()
    for option in dropdownBox.find_elements_by_tag_name('option'):
        if option.text == str(optionValue):
            print('found the option')
            time.sleep(.2)
            option.click()
            break

def purchased(gpu, price):
    print(Back.WHITE + Fore.GREEN + 'You have purchased a ' + Fore.GREEN + gpu['Model'] + Fore.BLUE + ' from ' + gpu['Website'] + Fore.BLUE + ' for ' + Fore.GREEN + '$' + price + Style.RESET_ALL)

def searchForElement(browser, id,searchId):
    return browser.find_element_by_xpath("//*[contains("+ id +", '"+ searchId + "')]")

def sendKeysToTextField(browser, id,searchId,textToType):
    return searchForElement(browser,'@id',searchId).send_keys(textToType)

def checkout(browser, gpu):
    if gpu['Website'] == 'BestBuy':
        #find elem that contains blah.sendKeys()
        waitForElementToLoad(browser, 'First Name')

        #fill in shipping info
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['fNameInputID'],checkOutInfoDict['fName'])
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['lNameInputID'],checkOutInfoDict['lName'])
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['addrInputID'],checkOutInfoDict['addr'])
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['cityInputID'],checkOutInfoDict['city'])
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['stateInputID'],checkOutInfoDict['state'])
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['zipInputID'],checkOutInfoDict['zip'])
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['emailInputID'],checkOutInfoDict['email'])
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['phoneInputID'],checkOutInfoDict['phone'])
        browser.find_element_by_class_name('btn-lg').click()

        #wait for page to load
        waitForElementToLoad(browser, 'Credit or Debit Card')
        #fill in billing info
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['ccInputID'],checkOutInfoDict['CC'])
        addr = searchForElement(browser,'@id',WebsiteInfo[gpu['Website']]['addrInputID'])
        city = searchForElement(browser,'@id',WebsiteInfo[gpu['Website']]['cityInputID'])
        zipcode = searchForElement(browser,'@id',WebsiteInfo[gpu['Website']]['zipInputID'])
        #highlight all text and replace it
        addr.send_keys(Keys.CONTROL + "a")
        addr.send_keys(checkOutInfoDict['bAddr'])
        city.send_keys(Keys.CONTROL + "a")
        city.send_keys(checkOutInfoDict['bCity'])
        zipcode.send_keys(Keys.CONTROL + "a")
        zipcode.send_keys(checkOutInfoDict['bZip'])
        #select element from dropdowns
        selectDropDown(browser.find_element_by_xpath("//*[contains(@id, '"+ WebsiteInfo[gpu['Website']]['expMonName'] + "')]"),checkOutInfoDict['expMon'])
        selectDropDown(browser.find_element_by_xpath("//*[contains(@id, '"+ WebsiteInfo[gpu['Website']]['expYearName'] + "')]"),checkOutInfoDict['expYear'])
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['ccSec'],checkOutInfoDict['sec'])

        #final checkout
        totalPrice = browser.find_elements_by_class_name('cash-money')[-1].text
        totalPriceInt = float(totalPrice.replace('$',''))
        if totalPriceInt < cashLimit:
            browser.browser.find_element_by_class_name('btn-primary').click()
            purchased(gpu, totalPriceInt)
            cashLimit -= totalPriceInt
            print('New Cash Limit is ' + Fore.GREEN + cashLimit + Fore.RESET)
            return True
        else:
            printError('Total GPU price was higher than your cash Limit')
            return False
    if gpu['Website'] == 'ASUS':
        fNameTextField = searchForElement(browser,'id',gpu['Website']['fNameInputID'])
        fNameTextField.click()
        fNameTextField.send_keys(Keys.ARROW_DOWN )
        fNameTextField.send_keys(Keys.ENTER)


    #browser.find_element_by_xpath('//button[text()="'+ 'Continue to Payment Information' + '"]').click()
    



def cart(browser, gpu):
    browser.get(WebsiteInfo[gpu['Website']]['cartLink']) #go to the page with your cart
    #waitForElementToLoad(browser, 'Your Cart')

    try:
        browser.find_element_by_xpath("//*[contains(text(), '"+ WebsiteInfo[gpu['Website']]['emptyCartText'] + "')]")
        printError('empty')
        return False
    except:
        if gpu['Website'] == 'BestBuy' or gpu['Website'] == 'ASUS':
            browser.find_element_by_xpath("//*[contains(text(), '"+ WebsiteInfo[gpu['Website']]['shippingButton'] + "')]").click()
        checkout(browser,gpu)




'''
    Loops through all open GPU tabs and checks if in stock then switches to the next tab if not in stock
'''
def stockCheckLoop(browser, GPUList):
    inStock = False
    index = 0
    while not inStock:
        gpu = GPUList[index]
        browser.switch_to.window(gpu['WindowHandle']) #open the gpus tab

        #BEGIN BESTBUY STOCK CHECK
        if gpu['Website'] == 'BestBuy':
            #if out of stock button exists
            try:
                addToCartBtn = browser.find_element_by_xpath('//button[text()="'+ WebsiteInfo[gpu['Website']]['OOSText'] + '"]')
                outOfStockPrint(gpu)
                browser.refresh()

            #if item is in stock click the first add to cart button
            except: 
                addToCartBtn = browser.find_element_by_class_name('btn-primary')

                #if the button does not say what the button should say i.e. BestBuy button should say Add to Cart but there is another button that says Sign Up
                if addToCartBtn.text != WebsiteInfo[gpu['Website']]['ISText']:
                    printError("The wrong button has been selected. This button says " + Fore.RED + addToCartBtn.text + Fore.RESET + ' it should say ' + Fore.BLUE + WebsiteInfo[gpu['Website']]['ISText'])
                    return False
                addToCartBtn.click()
                inStockPrint(gpu)
                time.sleep(delay)
                try:
                    searchForElement(browser, 'text()', 'Sorry')
                    index -= 1
                
                except:
                    cart(browser, gpu)
                    inStock = True
        #END BESTBUY STOCKCHECK
        if gpu['Website'] == 'ASUS':
            #if out of stock button exists
            try:    
                if not browser.find_element_by_xpath('//button[text()="'+ WebsiteInfo[gpu['Website']]['OOSText'] + '"]').is_enabled():
                    raise TypeError('item is in stock')

                outOfStockPrint(gpu)
                browser.refresh()
            except:
                addToCartBtn = browser.find_element_by_xpath('//button[text()="'+ WebsiteInfo[gpu['Website']]['ISText'] + '"]')

                #if the button does not say what the button should say i.e. BestBuy button should say Add to Cart but there is another button that says Sign Up
                if not addToCartBtn.is_enabled():
                    printError("The wrong button has been selected. This button says " + Fore.RED + addToCartBtn.text + Fore.RESET + ' it should say ' + Fore.BLUE + WebsiteInfo[gpu['Website']]['ISText'])
                    return False
                addToCartBtn.click()
                inStockPrint(gpu)
                time.sleep(delay)
                try:
                    searchForElement(browser, 'text()', 'Sorry')
                    index -= 1
                
                except:
                    cart(browser, gpu)
                    inStock = True
        #END ASUS STOCKCHECK

        #increment index after checking stock
        if index == len(GPUList)-1:
            index = 0
        else:
            index += 1

    #item was added to your cart

def seleniumFunc(GPUList):

    browser = webdriver.Chrome(driverPATH)

    #Setup Variables
    inStock = False

    #best buy
    soldOutText = 'Sold Out'
    inStockText = 'Add to Cart'

    #open all the tabs for the filtered graphics cards
    for gpu in GPUList:
        newTab(browser, gpu)
    browser.execute_script("window.close('data;');")
    
    print(GPUList)
    if not stockCheckLoop(browser, GPUList):
        printError('Problem in stockCheckLoop')
    



    time.sleep(10)

    '''
    while not inStock:
        try:
        #addToCartBtn = browser.find_element_by_class_name('btn-disabled')
            addToCartBtn = browser.find_element_by_xpath('//button[text()="'+ soldOutText + '"]')
            print('Out Of Stock')
            time.sleep(delay)
            browser.refresh()

  
        except: 
            addToCartBtn = browser.find_element_by_xpath('//button[text()="'+ inStockText + '"]')
            addToCartBtn.click()
            inStock = True
        '''
    


def welcomeMessage():
    print(Fore.MAGENTA + Style.BRIGHT + 'WELCOME TO GPU SCALPER 1.0 BY ' + Fore.CYAN +'IDGNFS' + Style.RESET_ALL)
    print('\n\n\n\n')

def start():
    welcomeMessage()
    global checkOutInfoDict
    checkOutInfoDict = getDict(checkoutPATH, True)[0]
    print(checkOutInfoDict['fName'])
    #gpuDict is a list of dictionaries
    gpuDict = getDict(spreadSheetPATH, False)
    if not gpuDict:
        printError('original GPU list is empty')

    filtGPU = filterDictionary(gpuDict,'Brand', 'ASUS', False)
    if not filtGPU:
        printError('Filtering GPU list returned an empty list, try changing values or check spelling')

    seleniumFunc(filtGPU)

init()
start()
deinit()