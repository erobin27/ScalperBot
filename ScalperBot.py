from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from colorama import init, deinit, Fore, Back, Style
import pickle
import os
from datetime import datetime


#colorama DOCS: https://pypi.org/project/colorama/
requiredFolders = ['Cookies','Spreadsheets']
searchMethod = ['link','page']
versionNumber = '1.1'
loadCookies = True
testingCheckout = False
testPage = 'https://www.newegg.com/p/pl?d=battery&LeftPriceRange=0+4'

driverPATH = "E:\MAIN\Programming\Projects\Scalper\chromedriver.exe"    #path to chromedriver for selenium
#spreadSheetPATH = 'E:\MAIN\Programming\Projects\Scalper\GPUS.csv'   #path to CSV file that contains the GPU info
#spreadSheetPATH = 'E:\MAIN\Programming\Projects\Scalper\Testing-ASUS.csv'
spreadSheetPATH = []
spreadsheets = []

pagesPATH = 'E:\MAIN\Programming\Projects\Scalper\GPUPages.csv'  
checkoutPATH = os.path.dirname(os.path.realpath(__file__)) + '\Spreadsheets\checkout.csv'
cookiePATH = os.path.dirname(os.path.realpath(__file__)) + '\Cookies\\'
checkOutInfoDict = {} 
cashLimit = 850
tabDelay = 2
delay = .5
#searchMethod = 'byGPUPage'
filterList = ['3070','3060','3080','3090','3060Ti']
WebsiteInfo = {
	'BestBuy' : {'Color' : 'Blue', 'OOSText' : 'Sold Out', 'ISText' : 'Add to Cart', 'cartLink' : 'https://www.bestbuy.com/checkout/r/fast-track', 'shippingButton':'Switch to Shipping', 'checkoutButtonText':'Checkout', 'ccInputID':'optimized-cc-card-number', 'expMonName':'expiration-month', 'expYearName':'expiration-year', 'ccSec':'credit-card-cvv','fNameInputID':'.firstName','lNameInputID':'.lastName','addrInputID':'.street','cityInputID':'.city','stateInputID':'.state','zipInputID':'.zipcode', 'emailInputID':'email', 'phoneInputID':'phone'},
    'Amazon' : {'Color' : 'Yellow', 'OOSText' : 'NULL', 'ISText' : 'NULL'},
	'NewEgg' : {'Color' : 'Orange', 'OOSText' : 'NULL', 'ISText' : 'Add to cart ', 'emptyCartText':'cart is empty', 'cartLink':'https://secure.newegg.com/shop/cart', 'shippingButton':'Continue With Guest Checkout'},
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

def uniqueElements(path, dtype='column', key='Website'):
    try:
        df = pd.read_csv(path)
    except:
        printError('Could not find csv file try changing the path')
        return None 

    if dtype == 'column':
        return df[key].unique()
    if dtype == 'headers':
        return list(df.columns.values) 
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

def filterDictionaryByRemoval(dictList, filterKey, filterValue):
    return list(filter(lambda x: x[filterKey] != filterValue, dictList))

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
    #print(gpu['Website'] + '_' + gpu['Model'] + " :" + Fore.RED + " OUT OF STOCK" + Fore.RESET)
    now = datetime.now()

    try:
        print('[' + now.strftime("%H:%M:%S") +  '] ' + gpu['Website'] + '_' + gpu['Model'] + " :" + Fore.RED + " OUT OF STOCK" + Fore.RESET)
    except: 
        print('[' + now.strftime("%H:%M:%S") +  '] ' + gpu['Website'] + " :" + Fore.RED + " OUT OF STOCK" + Fore.RESET)

def inStockPrint(gpu):
    now = datetime.now()
    
    try:
        print('[' + now.strftime("%H:%M:%S") +  '] ' + gpu['Website'] + '_' + gpu['Model'] + " :" + Fore.GREEN + " IN STOCK" + Fore.RESET)
    except: 
        print('[' + now.strftime("%H:%M:%S") +  '] ' + gpu['Website'] + " :" + Fore.GREEN + " IN STOCK" + Fore.RESET)

def waitForElementToLoad(browser, elemText):
    pageLoaded = False

    while not pageLoaded:
        try:
            browser.find_element_by_xpath("//*[contains(text(), '"+ elemText + "')]")
            print('waiting for '+ elemText)
            pageLoaded=True
        except:
            pageLoaded=False

def selectDropDown(dropdownBox, optionValue):
    dropdownBox.click()
    for option in dropdownBox.find_elements_by_tag_name('option'):
        if option.text.lower() == str(optionValue).lower():
            print('found the option')
            time.sleep(.2)
            option.click()
            break

def purchased(gpu, price):
    now = datetime.now()

    try:
        print('[' + now.strftime("%H:%M:%S") +  '] ' + Back.WHITE + Fore.BLACK + 'You have purchased a ' + Fore.GREEN + gpu['Model'] + Fore.BLACK + ' from ' + gpu['Website'] + Fore.BLACK + ' for ' + Fore.GREEN + '$' + str(price) + Style.RESET_ALL)
    except:
        print('[' + now.strftime("%H:%M:%S") +  '] ' + 'Bought Something for $' + Fore.GREEN + str(price) + Fore.RESET)
def searchForElement(browser, id,searchId):
    return browser.find_element_by_xpath("//*[contains("+ id +", '"+ searchId + "')]")

def searchForElements(browser, id,searchId):
    return browser.find_elements_by_xpath("//*[contains("+ id +", '"+ searchId + "')]")

def sendKeysToTextField(browser, id,searchId,textToType):
    return searchForElement(browser,id,searchId).send_keys(textToType)

def checkout(browser, gpu):
    global cashLimit
    cashLimit = cashLimit

    if gpu['Website'] == 'BestBuy':
        waitForElementToLoad(browser, 'Payment Information')
        #find elem that contains blah.sendKeys()
        sendKeysToTextField(browser,'@id',WebsiteInfo[gpu['Website']]['ccSec'],checkOutInfoDict['sec'])

        #final checkout
        totalPrice = browser.find_elements_by_class_name('cash-money')[-1].text
        totalPriceInt = float(totalPrice.replace('$',''))
        if totalPriceInt < cashLimit:
            #REMOVE THIS to buy on bestbuy
            #browser.find_element_by_class_name('btn-primary').click()
            print(browser.find_element_by_class_name('btn-primary').text)
            purchased(gpu, totalPriceInt)
            cashLimit -= totalPriceInt
            print('New Cash Limit is ' + Fore.GREEN + str(cashLimit) + Fore.RESET)
            #REMOVE THIS to get rid of wait after purchase
            input('Press Enter To Continue')
            return True
        else:
            printError('Total GPU price was higher than your cash Limit')
            return False

    #END BESTBUY
        
    if gpu['Website'] == 'ASUS':
        fNameTextField = searchForElement(browser,'id',gpu['Website']['fNameInputID'])
        fNameTextField.click()
        fNameTextField.send_keys(Keys.ARROW_DOWN )
        fNameTextField.send_keys(Keys.ENTER)
    if gpu['Website'] == 'NewEgg':
        try:
            searchForElement(browser,'text()','Continue to payment').click()
        except:
            printError('continue to payment not found (probably can skip it)')

        cvv = searchForElement(browser,'@class','form-text mask-cvv-4')
        cvv.click()
        
        try:
            cvv.send_keys(checkOutInfoDict['sec'])
        except Exception as e:
            print(e)
        #browser.find_element_by_class_name('form-text mask-cvv-4').sendKeys(checkOutInfoDict['sec'])
        
        try:
            searchForElement(browser,'text()','Review your order').click()
        except:
            printError('Review your order not found (probably place order instead)')

        prices = browser.find_elements_by_xpath("//strong")
        price = float(prices[-1].text)
        if price < cashLimit:
            print("total price is $" + str(price))
            #REMOVE THIS remove the comment to make it checkout for you
            #searchForElement(browser,'text()','Place Order').click()
            searchForElement(browser,'text()','Place Order').text
            return True
        else:
            printError('Cart is more than cash limit')
        #searchForElement(browser,'text()','Place Order').click()

        '''
        searchForElement(browser,'text()','Add New Address').click()
        time.sleep(1)
        sendKeysToTextField(browser,'@aria-label','First Name',checkOutInfoDict['fName'])
        sendKeysToTextField(browser,'@aria-label','Last Name',checkOutInfoDict['lName'])
        sendKeysToTextField(browser,'@aria-label','Address',checkOutInfoDict['addr'])
        sendKeysToTextField(browser,'@aria-label','City',checkOutInfoDict['city'])
        selectDropDown(browser.find_element_by_name('State'),checkOutInfoDict['stateLong'])
        
        sendKeysToTextField(browser,'@aria-label','Zip / Postal Code',checkOutInfoDict['zip'])
        sendKeysToTextField(browser,'@aria-label','Phone',checkOutInfoDict['phone'])
        sendKeysToTextField(browser,'@aria-label','Email',checkOutInfoDict['email'])
        searchForElement(browser,'text()','Save').click
        '''
    #browser.find_element_by_xpath('//button[text()="'+ 'Continue to Payment Information' + '"]').click()
    



def cart(browser, gpu):
    time.sleep(delay)
    browser.get(WebsiteInfo[gpu['Website']]['cartLink']) #go to the page with your cart
    time.sleep(delay)
    
    
    #waitForElementToLoad(browser, 'Your Cart')
    try:
        browser.find_element_by_xpath("//*[contains(text(), '"+ WebsiteInfo[gpu['Website']]['emptyCartText'] + "')]")
        browser.refresh()
        browser.find_element_by_xpath("//*[contains(text(), '"+ WebsiteInfo[gpu['Website']]['emptyCartText'] + "')]")
        printError('empty')
        return 'empty'
    except:
        if gpu['Website'] == 'NewEgg':
            complete = False
            while not complete:
                try:
                    time.sleep(delay)
                    searchForElement(browser,'text()','Secure Checkout').click()
                    time.sleep(delay)
                    #browser.find_element_by_xpath("//*[contains(text(), '"+ WebsiteInfo[gpu['Website']]['shippingButton'] + "')]").click()
                    complete=True
                    
                except:
                    time.sleep(delay)
                    browser.find_element_by_class_name('close').click()
    #TODO: Reorganize this
        if gpu['Website'] == 'BestBuy' or gpu['Website'] == 'ASUS':
            try:
                browser.find_element_by_xpath("//*[contains(text(), '"+ WebsiteInfo[gpu['Website']]['shippingButton'] + "')]").click()
            except:
                print('no button to click')
                check = checkout(browser,gpu)
                if check:
                    return True
                else:
                    printError('Problem in checkout')
                    return False

            check = checkout(browser,gpu)
            if check:
                return True
            else:
                printError('Problem in checkout')
                return False
    return True


def filterPages(browser,p):
    browser.switch_to.window(p['WindowHandle']) #open the page tab
    time.sleep(tabDelay)

    #if the website has filters go through and filter the website
    for filters in filterList:
        if p['Website'] == 'BestBuy':
            if filters == '3060':
                searchForElements(browser, '@id',str(p[filters]))[1].click()
            elif filters == '3060Ti':
                searchForElements(browser, '@id',str(p[filters]))[0].click()
            else:
                searchForElement(browser, '@id',str(p[filters])).click()
            #time.sleep(tabDelay)

    #NewEgg has filters but you cannot easily click them so I leave it out of the forloop for now        
    if p['Website'] == 'NewEgg':
        searchForElement(browser, 'text()','GeForce RTX 30 Series').click()
        browser.find_element_by_xpath('//button[text()="'+ ' Apply' + '"]').click()
        priceLimit = searchForElement(browser, '@aria-label','price to')
        priceLimit.click()
        priceLimit.send_keys(cashLimit)
        browser.find_element_by_xpath('//button[text()="'+ ' Apply' + '"]').click()
    time.sleep(1)
'''
    while not inStock:
        page = PageList[index]
        browser.switch_to.window(page['WindowHandle']) #open the page tab
        if testingCheckout:
            browser.get(testPage)
        #in stock:
        try:
            addToCartBtn = browser.find_element_by_xpath('//button[text()="'+ WebsiteInfo[page['Website']]['ISText'] + '"]')
            addToCartBtn.click()
            inStockPrint(page)
            if cart(browser, page):
                inStock = True

        except:
            outOfStockPrint(page)
            browser.refresh()

        if index == len(PageList)-1:
            index = 0
        else:
            index += 1
'''
def filterLink(browser, GPUList):
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
'''
    Loops through all open GPU tabs and checks if in stock then switches to the next tab if not in stock
'''
def stockCheckLoop(browser, gpu):

    browser.switch_to.window(gpu['WindowHandle']) #open the gpus tab
    browser.refresh()
    try:
        addToCartBtn = browser.find_element_by_xpath('//button[text()="'+ WebsiteInfo[gpu['Website']]['ISText'] + '"]')
        addToCartBtn.click()
        inStockPrint(gpu)
        res = cart(browser, gpu)

        #this will keep trying to add item to cart until the item is displayed as out of stock
        if res == 'empty':
            printError('Cart is empty, Retrying')
            browser.execute_script("window.history.go(-1)") #go back 1 page if cart is empty
            stockCheckLoop(browser, gpu)
        elif res: #if successfully checked out
            browser.get(gpu['URL'])
        elif not res: #if error occurred 
            stockCheckLoop(browser, gpu)

    except:
        outOfStockPrint(gpu)

def seleniumFunc():
    browser = webdriver.Chrome(driverPATH)

    for cookieFile in os.listdir(cookiePATH):
        loadCookiesFunc(browser, cookieFile.replace('Cookies.pkl',''))
    #loginToWebsite(browser, ['NewEgg'])
    #loadCookies(browser)
    #browser.get('https://secure.newegg.com/shop/cart')
    #for cookie in pickle.load(open('NewEggCookies.pkl',"rb")):
    #    browser.add_cookie(cookie)

    #Setup Variables
    inStock = False
    #open all the tabs for the filtered graphics cards
    

    #What we need to happen:
    #GPU Pages filters all pages correctly
    #GPU links open all links
    #loop a refresh and check for available button
    #This for loops opens all the tabs and sets up all of the fitlers for each page
    firstLoop = True
    for sheet in spreadsheets:
        if sheet['method'] == 'link':
            pass

        #open each page
        #close default page
        for page in sheet['gpuDictList']:
            #open the tabs in the dictionary
            newTab(browser, page)
            #add cookies to the tabs if they exist
            
            if sheet['method'] == 'page':
                filterPages(browser,page)
            
        '''
        if sheet['method'] == 'page':
            for page in sheet['gpuDictList']:
                newTab(browser, page)
            browser.execute_script("window.close('data;');")
        '''
        if firstLoop:
            browser.switch_to.window(browser.window_handles[0])
            browser.close()
            browser.switch_to.window(browser.window_handles[0])
            firstLoop = False
        #open each page
        #send that page to stock check loop
        #if sheet['method'] == 'page':
        #    filterPages(browser,sheet['gpuDictList'])
    
    #loop through all open tabs refresh and check for stock
    sheetIndex=0
    loopSheets=True
    while loopSheets:
        for gpu in spreadsheets[sheetIndex]['gpuDictList']:
            #REMOVE THIS
            stockCheckLoop(browser,gpu)


        if sheetIndex == len(spreadsheets)-1:
            sheetIndex = 0
        else:
            sheetIndex += 1

    time.sleep(10)
    '''
    if curr['gpuDict'] == 'byLink':
        for gpu in GPUList:
            newTab(browser, gpu)
        browser.execute_script("window.close('data;');")
        
        print(GPUList)
        if not stockCheckLoop(browser, GPUList):
            printError('Problem in stockCheckLoop')
    
    if curr['method'] == 'page':
        for page in curr:
            newTab(browser, page)
        browser.execute_script("window.close('data;');")

        if not stockCheckLoop(browser, GPUList):
            printError('Problem in stockCheckLoop')
    '''

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
    print(Fore.MAGENTA + Style.BRIGHT + 'WELCOME TO GPU SCALPER v' + versionNumber + ' BY ' + Fore.CYAN +'IDGNFS' + Style.RESET_ALL)
    print(Fore.GREEN + 'BestBuy ' + Fore.RED + 'Amazon ' + Fore.GREEN + 'NewEgg ' + Fore.RED + 'ASUS ' + Fore.RED + 'Zotac ' + Fore.RED + 'B&H ' + Fore.RED + Fore.RED + 'Adorama ' + Fore.RESET)
    print('\n')

def userQuestion(question, choices,limit=True,help=None):
    fullQuestion = question

    if help:    #if help is true then print a 0 option too
        r = range(-1,len(choices))
    else:
        r = range(len(choices))

    for choiceIndex in r:
        if choiceIndex == -1:
            fullQuestion+='\n\t'
            fullQuestion+= Fore.YELLOW +str(choiceIndex+1) + ') '+Fore.RESET
            fullQuestion+=help
        else:
            fullQuestion+='\n\t'
            fullQuestion+= Fore.BLUE +str(choiceIndex+1) + ') '+Fore.RESET
            fullQuestion+=str(choices[choiceIndex])

        if choiceIndex ==len(choices)-1:
            fullQuestion += '\n\n'

    complete = False
    response = 0
    if limit:
        while not complete:
            try:
                response = int(input(fullQuestion))
            except:
                printError('Input a number not text')
            
            if help:
                if response == -1:
                    terminate()
                if response > len(choices) or response < -1:
                    printError('incorrect input try again')
                else:
                    complete = True
            else:
                if response == -1:
                    terminate()
                if response > len(choices) or response < 1:
                    printError('incorrect input try again')
                else:
                    complete = True
    else:
        response = input(fullQuestion)
    return response

def terminate():
    print(Fore.RED + 'T', end='')

    for letter in 'ERMINATING':
        print(letter, end='')
        time.sleep(.1)
    time.sleep(.5)
    print('.', end='')
    time.sleep(.5)
    print('.', end='')
    time.sleep(.5)
    print('.' + Fore.RESET)
    quit()

#could cause errors if file has the name of a key without having a . extension
#could cause errors if multiple folders exist   
def checkForFolders(dirList, folderKeys):
    haveFolders = True
    for key in folderKeys:
        if key not in dirList:
            filepath = str(os.path.dirname(os.path.realpath(__file__)))
            os.mkdir(filepath + '\\' + key)
            print('Created ' + Fore.GREEN + key + Fore.RESET + ' folder in: ' + Fore.GREEN + os.path.dirname(os.path.realpath(__file__)) + '\\' + key + Fore.RESET)
            haveFolders = False
    
    return haveFolders

def addSpreadsheet():
    fileLoc = os.path.dirname(os.path.realpath(__file__))
    
    spreadsheetList = os.listdir(fileLoc + '\Spreadsheets')
    res = userQuestion('What spreadsheet would you like to use?',spreadsheetList)
    sheet = spreadsheetList[res-1]
    path = fileLoc + '\\Spreadsheets\\' + sheet

    res = userQuestion('What method would you like to use for ' + sheet + '?',['Search by individual link','Search by GPU Page'])
    method=searchMethod[res-1]

    removeWebsites = []
    if searchMethod[res-1] == 'page':
        elements = uniqueElements(path)
        res = userQuestion('If you would like to skip a website in the list please type the number seperated by spaces. Otherwise type 0.',elements,False)
        for index in res.split():
            index = int(index)
            if index > len(elements) or index < 0:
                printError('out of bounds')
                break
            if index == 0:
                break
            removeWebsites.append(elements[index-1])
            
    spreadsheets.append({'path': path, 'method':method, 'remove': removeWebsites, 'name':sheet, 'cookiePath': fileLoc + '\Cookies'})    

def sleepWithCount(amount):
    if amount < 1:
        return None

    for i in range(amount,-1,-1):
        if i < 10:
            print('\t' + Fore.RED + ' ' +str(i) + Fore.RESET, end='\r')
        else:
            print('\t' + Fore.RED + str(i) + Fore.RESET, end='\r')
        time.sleep(1)

def loadCookiesFunc(browser, website):
    #open newtab with cookies matching current cookies
    #load cookies
    try:
        loginPATH = os.path.dirname(os.path.realpath(__file__)) + '\SpreadSheets' + '\LoginPages.csv'
        pageLinks = []
        websites = uniqueElements(loginPATH)
        df = pd.read_csv(loginPATH)
        df.set_index('Website',inplace=True)

        loginDict = df.to_dict()['LoginPage']
        browser.get(loginDict[website])

        print('Loading Cookies for ' + Fore.BLUE + website + Fore.RESET)

        cookies = pickle.load(open(cookiePATH + website + 'Cookies.pkl',"rb"))
        for cookie in cookies:
            browser.add_cookie(cookie)
        
    except Exception as e:
        print(e)
        print('No Cookies were found for ' + Fore.RED + website + Fore.RESET)
    



def createCookies(): 
    #sleepWithCount(30)
    loginPATH = os.path.dirname(os.path.realpath(__file__)) + '\SpreadSheets' + '\LoginPages.csv'
    pageLinks = []
    websites = uniqueElements(loginPATH)
    df = pd.read_csv(loginPATH)
    df.set_index('Website',inplace=True)
    loginDict = df.to_dict()['LoginPage']
    res = userQuestion('Which website would you like to save cookies for? enter numbers seperated by spaces.', websites) - 1
    browser = webdriver.Chrome(driverPATH)
    browser.get(loginDict[websites[res]])
    print('\n\n ')
    input('Once you finish logging into ' + websites[res] + ' press enter to save your cookies.')
    pickle.dump(browser.get_cookies(), open(os.path.dirname(os.path.realpath(__file__)) + '\Cookies\\' + websites[res] + 'Cookies.pkl',"wb"))
    browser.close()
        
    print('Your cookies for ' + Fore.GREEN + websites[res] + Fore.RESET + ' have been saved to:')
    print(Fore.BLUE + os.path.dirname(os.path.realpath(__file__)) + '\Cookies\\' + websites[res] + 'Cookies.pkl' + Fore.RESET)
    
    #pickle.dump(browser.get_cookies(), open(websiteName + '.pkl',"wb"))
    #browser.close()
    '''
    for website in webList:
        if website == 'NewEgg':
            browser.execute_script("window.open('" + 'https://secure.newegg.com/shop/cart' + "');")
            browser.switch_to.window(browser.window_handles[-1])
            time.sleep(2)
            try:
                browser.find_element_by_class_name('close').click()
            except:
                searchForElement(browser,'text()','Sign in').click()
                browser.find_element_by_name('signEmail').send_keys(checkOutInfoDict['email'])
                browser.find_element_by_name('signIn').click()
                #browser.find_element_by_name('password').send_keys(checkOutInfoDict['passw'])
                time.sleep(20)
                pickle.dump(browser.get_cookies(), open('NewEggCookies.pkl',"wb"))
                browser.close()

    '''

def printTopic(topic, description):
    print(Fore.YELLOW + topic + Fore.RESET)
    print('\t' + description)

def help():
    print('----------------------------------------------------------------------')
    print(Fore.YELLOW + '\t\t\tHELP SECTION\n' + Fore.RESET)

    printTopic('NewEgg Cookies', 'NewEgg requires you to have an account with Credit Card info, Billing, and\n\tShipping already on it. You must then create cookies for newegg by logging in\n\tthen load the cookies when you start.')
    printTopic('Why use cookies?', 'Cookies allow you to save information like login info so you can automatically\n\tbe logged into a website and reduce the amount of input required by\n\tusing autofill.')
    printTopic('Search By Pages', 'Search by pages uses the websites GPU page then filters the search results\n\tfrom there and can check multiple GPUs stock at once and buy the first one\n\tthat comes available. Faster than single link.')
    printTopic('Search By Link', 'Search by link uses one specific link to check for a single GPU')
    
    print('\n')
    print(Fore.YELLOW +'\t\t    SCROLL UP TO VIEW HELP'+ Fore.RESET)
    print('----------------------------------------------------------------------\n')

def setup():
    fileLoc = os.path.dirname(os.path.realpath(__file__))
    if not checkForFolders(os.listdir(fileLoc),requiredFolders):
        printError('You did not have the required folders, they have been created')
        print(requiredFolders)
        print('\n')
    global loadCookies
    while True:
        if spreadsheets and loadCookies:
            actions = ['Add Spreadsheet','Create Cookies','Disable Cookies','Start']
        elif spreadsheets and not loadCookies:
            actions = ['Add Spreadsheet','Create Cookies','Enable Cookies','Start']
        elif not spreadsheets and loadCookies:
            actions = ['Add Spreadsheet','Create Cookies','Disable Cookies']
        else:
            actions = ['Add Spreadsheet','Create Cookies','Enable Cookies']

        res = userQuestion('Please select an action.',actions,True,'Help')
        if res == 0:
            help()
        if res == 1:
            addSpreadsheet()
        if res == 2:
            createCookies()
        if res == 3:
            loadCookies = not loadCookies
            if loadCookies:
                print('You have to chose to' + Fore.GREEN +' USE '+ Fore.RESET + 'cookies this will help checkout on websites like NewEgg faster.')
            else:
                print('You have to chose to' + Fore.RED +' NOT USE '+ Fore.RESET + 'cookies this will disable the ability to checkout on NewEgg.')
        if res == 4:
            if getDict(checkoutPATH, False) == None:
                printError('checkout path is invalid make sure you have a checkout.csv file in your Spreadsheets folder')
                printError('No checkout info, will not be able to buy anything')
            else:
                global checkOutInfoDict
                checkOutInfoDict = getDict(checkoutPATH, False)[0]

            break
        
        #options.append(int(input('What spreadsheet would you like to use?\n\t1) GPU Link List\n\t2) GPU Page List\n\t3) Testing List\n\n')))
        #options.append(int(input('What method would you like to use for this spreadsheet?\n\t1) Search by individual link\n\t2) Search by GPU Page')))

'''
    #gpuDict: the dictionary that stores all the info
    #headers: the top row of the spreadsheet (categories) i.e. Brand, Model, MSRP
    #columns: the values underneath the headers on the spreadsheet i.e. Brand: ASUS, EVGA, MSI
'''
def start():
    welcomeMessage()

    setup()


    global checkOutInfoDict
    #for each spreadsheet that is loaded if you want to filter it down to more specific stuff do so then write gpuDict
    for sheet in spreadsheets:
        gpuDict = getDict(sheet['path'], False)
        if not gpuDict:
            printError('Spreadsheet is empty')
        res = userQuestion('Would you like to filter ' + sheet['name'] + '?',['Yes', 'No'])
        if res == 1:
            filtering = True
            while filtering:
                headers = uniqueElements(sheet['path'],'headers')
                res = userQuestion('which subject would you like to filter by?',headers)
                headerSelection = headers[res-1]
                columns = uniqueElements(sheet['path'],'column',headerSelection)
                res = userQuestion('which '+ headerSelection +' would you like to filter by?',columns)
                columnSelection = columns[res-1]
                gpuDict = filterDictionary(gpuDict,headerSelection,columnSelection,True)
                res = userQuestion('Would you like to filter ' + sheet['name'] + ' further?',['Yes','No'])
                if res == 2:
                    filtering = False
        sheet['gpuDictList'] = gpuDict
        


    print(Fore.MAGENTA + "READY TO BEGIN GPU SCALPER v" + versionNumber + Fore.RESET)
    print('--------------USING--------------')
    for sheet in spreadsheets:
        print(sheet['name'] + ' : ' + Fore.BLUE + sheet['method'] + ' method' + Fore.RESET)
    print(Fore.GREEN + '--------------BEGIN SCALPING--------------' + Fore.RESET)
    seleniumFunc()
'''
    if searchMethod == 'byLink':
        gpuDict = getDict(spreadSheetPATH, False)
        if not gpuDict:
            printError('original GPU list is empty')

        filtGPU = filterDictionary(gpuDict,'Brand', 'ASUS', False)
        if not filtGPU:
            printError('Filtering GPU list returned an empty list, try changing values or check spelling')

        seleniumFunc(filtGPU)

    if searchMethod == 'byGPUPage':
        pageDict = getDict(pagesPATH, True)
        pageDict = filterDictionary(pageDict,'Website', 'BestBuy', True)
        if not pageDict:
            printError('Page list is empty')
        seleniumFunc(pageDict)
'''
init()
start()
deinit()









#BestBuy Checkoutwith no account
'''
        #fill in shipping info
        try:
            print(checkOutInfoDict['fName'])
        except Exception as e:
            print(e)
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
        if totalPriceInt < budget:
            #REMOVE THIS to buy on bestbuy
            #browser.find_element_by_class_name('btn-primary').click()
            purchased(gpu, totalPriceInt)
            budget -= totalPriceInt
            print('New Cash Limit is ' + Fore.GREEN + budget + Fore.RESET)
            return True
        else:
            printError('Total GPU price was higher than your cash Limit')
            return False
    '''