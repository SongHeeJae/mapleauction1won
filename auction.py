import pyautogui as pag
from time import sleep
import random
import pytesseract as pt
import re
from PIL import Image, ImageGrab

pt.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

btn_gap1 = 55 # X 버튼 좌표 간격
btn_gap2 = 50 # 장비탭 버튼 좌표 간격

conf = 0.9 # 이미지 인식률 따라서 조정 . 컴퓨터마다 실행해보고 조절하면됨 E똥컴이거나 서버느리면  이거 2~3으로하셈
search_delay = 2 # 검색 딜레이 서버 상황에 따라 조정. 검색 엔터 누르고 난 뒤의 대기
open_delay = 5 # 경매장 첫 입장 딜레이 . 이것도 제뉴어리 83 최저간데 왜저거 63으로나옴 그럼? 인시굼ㄴ젠가봄 어차피 1원씩내리긴하는데 ㄱㄷ 수정좀해봄
delay = 1000 # 한텀 끝나고 휴식기간(초)

tab_str = ["장비", "소비", "설치", "기타", "캐시"]

class Item:

    # 종류, 경로, 이름, 가격, 수량, 최소금액
    def __init__(self, tab, path, name, price, amount, minPrice) :
        self.tab = tab
        self.path = path
        self.name = name
        self.price = price
        self.amount = amount
        self.minPrice = minPrice

class Auction:

    def __init__(self, items) :
        self.items = items
    

    def open(self) :
        pag.click(pag.locateCenterOnScreen('.\\img\\menu.PNG', confidence=conf))
        sleep(0.5)
        pag.click(pag.locateCenterOnScreen('.\\img\\auction.PNG', confidence=conf))
        sleep(3)

    def run(self) :

        modify_idx = [] # 가격 수정할 인덱스
        
        # 검색 시작
        for i in range(len(self.items)) :
            item = self.items[i]
            pag.click(self.search_pos)
            pag.typewrite(item.name)
            pag.press('enter')
            sleep(1)
            pag.press('enter')

            sleep(search_delay)

            if item.tab == '장비' or item.tab == '캐시' :
                img = ImageGrab.grab(self.price_pos1) # 가격 확인
            else:
                img = ImageGrab.grab(self.price_pos2) # 개당 가격 확인

            price = self.image_to_string(img)

            if price < item.price and price >= item.minPrice :
                modify_idx.append(i)
                item.price = price - 1
            
            self.eraseText()

            sleep(5-search_delay)
        
        # 임시 데이터
        # price = 130000
        # modify_idx = [0,1,2,3,4,5,6,7]
        if len(modify_idx) == 0 :
            return
        
       
        # 판매탭 이동
        pag.click(self.sell_pos)

        sleep(2)

        # 물품 취소
        modify_idx.reverse()

        page = 0 # 현재 페이지

        for i in modify_idx :
            next_page = i//6
            self.nextPage(next_page - page)
            sleep(1)
            page = next_page
            item = self.items.pop(i)
            pag.click((self.cancel_pos[0], self.cancel_pos[1] + (i%6) * btn_gap1))
            sleep(0.5)
            pag.press('enter')
            sleep(1.5)
            self.items.append(item)

        # 물품 수령
        self.waitItem()

        # 수령 물품 업로드
        for i in range(len(self.items) - len(modify_idx), len(self.items)) :
            item = self.items[i]
            tab_pos = self.tabs_pos[item.tab]
            pag.click(tab_pos)
            sleep(0.5)

            pag.click(pag.locateCenterOnScreen(item.path, confidence=conf))
            sleep(0.5)
            pag.click(self.drop_pos)
            sleep(0.5)
            if item.tab == '장비' or item.tab == '캐시' :
                pag.click(pag.locateCenterOnScreen('.\\img\\sell_price1.PNG', confidence=conf))
                sleep(0.5)
                pag.typewrite(str(item.price))
            else :
                pag.click(pag.locateCenterOnScreen('.\\img\\sell_amount.PNG', confidence=conf))
                sleep(0.5)
                pag.typewrite(item.amount)
                sleep(0.5)
                pag.click(pag.locateCenterOnScreen('.\\img\\sell_price2.PNG', confidence=conf))
                pag.typewrite(str(item.price))

            sleep(0.5)

            pag.click(pag.locateCenterOnScreen('.\\img\\sell_ok.PNG', confidence=conf))
            sleep(0.5)
            pag.press('enter')
            sleep(0.5)
            pag.press('enter')
            sleep(0.5)
            pag.press('enter')
            sleep(3)

    def nextPage(self, p) :
        if p > 0 :
            for i in range(p):
                sleep(1)
                pag.click(self.next_pos)
        elif p < 0 :
            p *= -1
            for i in range(p) :
                sleep(1)
                pag.click(self.prev_pos)


    def waitItem(self) :
        pag.click(self.clear_pos)
        sleep(1)
        pag.click(pag.locateCenterOnScreen('.\\img\\return.PNG', confidence=conf))
        sleep(1)
        pag.press('enter')
        
        while True :
            sleep(1)
            warning = pag.locateCenterOnScreen('.\\img\\warning.PNG', confidence=conf)
            if warning != None : break
        sleep(1)
        pag.press('enter')
        sleep(1)
        pag.click(self.sell_pos)

    def eraseText(self) :
        for i in range(5) :
            pag.click(self.search_pos)
            pag.press(['backspace', 'backspace', 'backspace', 'backspace', 'backspace'])
        pass


    def loof(self, delay) :
        flag = True

        while True:
            # 경매장 입장
            self.open()
            sleep(open_delay)

            # 좌표값 초기화
            if flag :
                self.initPos()

            # 실행
            self.run()

            # 경매장 퇴장
            self.close()

            flag = False

            random_delay = random.random() * 300
            random_delay *= random.random() > 0.5 and 1 or -1
            random_delay = delay + random_delay < 10 and 10 or random_delay + delay
            sleep(random_delay)

    def close(self) :
        pag.press('esc')
        sleep(1)
        pag.press('enter')

    def initPos(self) :
        # 좌표값들 초기화

        x, y = pag.locateCenterOnScreen('.\\img\\search.PNG', confidence=conf) # 검색
        rand = self.random_pos()
        self.search_pos = (x + rand[0], y + rand[1])

        self.price_pos1 = pag.locateCenterOnScreen('.\\img\\price1.PNG', confidence=conf) # 가격
        self.price_pos1 = (self.price_pos1.x - 70, self.price_pos1.y + 27)
        self.price_pos1 += (self.price_pos1[0] + 125, self.price_pos1[1] + 19)

        sleep(0.5)

        self.price_pos2 = pag.locateCenterOnScreen('.\\img\\price2.PNG', confidence=conf) # 개당 가격
        self.price_pos2 = (self.price_pos2.x - 70, self.price_pos2.y + 27)
        self.price_pos2 += (self.price_pos2[0] + 125, self.price_pos2[1] + 19)

        sleep(0.5)

        x, y = pag.locateCenterOnScreen('.\\img\\sell.PNG', confidence=conf) # 판매 탭
        rand = self.random_pos()
        self.sell_pos = (x + rand[0], y + rand[1])
        pag.click(self.sell_pos)
        sleep(0.5)
        x, y = pag.locateCenterOnScreen('.\\img\\cancel.PNG', confidence=conf) # 판매 취소 버튼
        self.cancel_pos = x, y
        
        self.tabs_pos = {}
        
        sleep(0.5)
        x, y = pag.locateCenterOnScreen('.\\img\\tab1.PNG', confidence=conf) # 장비 탭 버튼
        for i in range(5) :
            self.tabs_pos[tab_str[i]] = (x + i, y + i * btn_gap2)


        self.clear_pos = pag.locateCenterOnScreen('.\\img\\clear.PNG', confidence=conf) # 완료 탭
        self.drop_pos = pag.locateCenterOnScreen('.\\img\\drop.PNG', confidence=conf) # 드래그앤드롭
        self.next_pos = pag.locateCenterOnScreen('.\\img\\next.PNG', confidence=conf) # 판매 템 다음페이지
        self.prev_pos = pag.locateCenterOnScreen('.\\img\\prev.PNG', confidence=conf) # 판매 템 이전페이지

    def dfs(self, img, visited, x, y, dx, dy) :
        visited[x][y] = True
        c = 1
        for i in range(8) :
            nx = x + dx[i]
            ny = y + dy[i]
            if img.getpixel((nx, ny)) == (255,255,255) and visited[nx][ny] == False :
                c += self.dfs(img, visited, nx, ny, dx, dy) * c + i
        return c

    def getImageNumber(self, n) : # 방문한 픽셀로 숫자 계산
        if n == 55 : return 0
        elif n == 71 : return 1
        elif n == 1654 : return 2
        elif n == 738 : return 3
        elif n == 85 : return 4
        elif n == 848 : return 5
        elif n == 68 : return 6
        elif n == 220 : return 7
        elif n == 883 : return 8
        elif n == 217 : return 9 

    def image_to_string(self, img) : # 이미지에서 가격 뽑아내기
        width, height = img.size

        price = 0

        dx = [0,0,-1,1, 1, 1, -1, -1]
        dy = [1,-1,0,0, -1, 1, -1, 1]
        visited = [[False for _ in range(height)] for _ in range(width)]
        h = int(height/2)
        for i in range(width):
            if img.getpixel((i, h)) == (255, 255, 255) and visited[i][h] == False:
                n = self.getImageNumber(self.dfs(img, visited, i, h, dx, dy))
                price = price * 10 + n
                  
        print(price)
        return price


        """
        for y in range(height) :
            for x in range(width) :
                if (255,255,255) != img.getpixel((x, y)) :
                    img.putpixel((x, y), (255,255,255))

                else :
                    img.putpixel((x, y), (0,0,0))
        img = img.resize((width, height))
        img.save('test.jpg')
        price_str = pt.image_to_string(img, lang='kor')
        print(price_str)
        price = re.findall('\d+', price_str)
        price = ''.join(price)
        print("price:" + price)
        return int(price)
        """

    def random_pos(self): # 랜덤위치
        return random.random() > 0.5 and (random.random() * 10, random.random() * -2) or (random.random() * -10, random.random() * 2)


if __name__ == '__main__' :
    items = []
    # items.append(Item('장비', '.\\item_image\\1.PNG','xkdnjdlsgpstmfld', 99999999, '1', 99000000))

ㅡ음    # '아이템종류', '아이템이미지', '아이템명영어로', 현재가격, '수량', 최소가격
    # 이 순서로 넣으면댐
    # 따옴표 구분하고
    # 파일명도 니 원하는거로 넣어도댐
    items.append(Item('소비', '.\\item_image\\4.PNG', 'tntkdgkszbqm', 100000, '1', 110000))
    items.append(Item('소비', '.\\item_image\\4.PNG', 'tntkdgkszbqm', 126000, '1', 110000))
    items.append(Item('소비', '.\\item_image\\4.PNG', 'tntkdgkszbqm', 126000, '1', 110000))
    items.append(Item('소비', '.\\item_image\\4.PNG', 'tntkdgkszbqm', 126000, '1', 110000))
    items.append(Item('소비', '.\\item_image\\4.PNG', 'tntkdgkszbqm', 126000, '1', 110000))
    items.append(Item('소비', '.\\item_image\\4.PNG', 'tntkdgkszbqm', 126000, '1', 110000))
    items.append(Item('소비', '.\\item_image\\4.PNG', 'tntkdgkszbqm', 126000, '1', 110000))
    items.append(Item('소비', '.\\item_image\\4.PNG', 'tntkdgkszbqm', 126000, '1', 110000))

    
    auction = Auction(items)

    auction.loof(delay)
