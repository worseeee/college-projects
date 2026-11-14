class Employee():
    name='机电厂员工'
    count=0
    def __init__(self,name,salary):
        self.employee_name=name
        self.employee_salary=salary
        Employee.count+=1
    def __del__(self):
        print("已被删除")
        Employee.count-=1
    def display_count(self):
        print("员工总人数：%d人"%Employee.count)
    def display_employee(self):
        print(self.employee_name,"\n",self.employee_salary)
