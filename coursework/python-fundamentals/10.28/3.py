class Dish:
    def __init__(self,name,price,id):
        self.name=name
        self.price=price
        self.id=id

class Menu():
    def __init__(self):
        self.dishes=[]
    def add_dish(self,dish):
        self.dishes.append(dish)
    def display_menu(self):
        print('菜单列表：')
        for dish in self.dishes:
            print(dish.name,'-'*10,dish.price,'-'*10,dish.id)

class Order():
    def __init__(self):
        self.dishes=[]
    def add_dish(self,dish):
        self.dishes.append(dish)
    def display_order(self):
        print('订单列表：')
        for dish in self.dishes:
            print(dish.name,'-'*10,dish.price)
    def calculate(self):
        self.total=0
        for dish in self.dishes:
            self.total+=dish.price
        print(f'总金额：{self.total}元')
        
def main():
    dish1=Dish('宫保鸡丁',30,0)
    dish2=Dish('鱼香肉丝',35,1)
    dish3=Dish('红烧鲫鱼',38,2)
    menu=Menu()
    menu.add_dish(dish1)
    menu.add_dish(dish2)
    menu.add_dish(dish3)
    menu.display_menu()
    s=[]
    while True:
        a=eval(input('请选择菜品编号：（按10提交）'))
        if a==10:
            break
        else:
            s.append(a)
    order=Order()
    for i in s:
        order.add_dish(menu.dishes[i])
    order.display_order()
    order.calculate()
