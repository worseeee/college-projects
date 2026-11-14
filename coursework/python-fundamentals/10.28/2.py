class account():
    count=0
    def __init__(self,name,num,save):
        self.account_name=name
        self.account_num=num
        self.account_save=save
        account.count+=1
    def display_count(self):
        print('开户总人数：%d人'%account.count)
    def search(self):
        print(f'{self.account_name}的余额为：{self.account_save}')
    def add(self):
        add=eval(input('请输入您将存款的数额：'))
        self.account_save+=add
        print('存款成功！')
    def dec(self):
        dec=eval(input('请输入您将取款的数额：'))
        self.account_save-=dec
        print('取款成功！')
