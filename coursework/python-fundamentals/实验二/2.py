class Student:
    """学生类，用于存储单个学生的基本信息"""
    
    def __init__(self, student_id, name, age, grade):
        """
        初始化学生对象
        Args:
            student_id: 学号
            name: 姓名
            age: 年龄
            grade: 成绩
        """
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade
    
    def display_info(self):
        """显示学生信息"""
        print(f"学号: {self.student_id}, 姓名: {self.name}, 年龄: {self.age}, 成绩: {self.grade}")
    
    def update_info(self, name=None, age=None, grade=None):
        """更新学生信息"""
        if name:
            self.name = name
        if age:
            self.age = age
        if grade:
            self.grade = grade
        print("学生信息更新成功！")


class StudentManagementSystem:
    """学生管理系统类，用于管理所有学生信息"""
    
    def __init__(self):
        """初始化系统，创建空的学生字典"""
        self.students = {}
    
    def add_student(self, student_id, name, age, grade):
        """
        添加学生
        Args:
            student_id: 学号
            name: 姓名
            age: 年龄
            grade: 成绩
        """
        if student_id in self.students:
            print("该学号已存在！")
            return False
        self.students[student_id] = Student(student_id, name, age, grade)
        print("学生添加成功！")
        return True
    
    def search_student(self, student_id):
        """根据学号查询学生"""
        if student_id in self.students:
            self.students[student_id].display_info()
            return self.students[student_id]
        else:
            print("未找到该学生！")
            return None
    
    def update_student(self, student_id, name=None, age=None, grade=None):
        """更新学生信息"""
        if student_id in self.students:
            self.students[student_id].update_info(name, age, grade)
            return True
        else:
            print("未找到该学生！")
            return False
    
    def delete_student(self, student_id):
        """删除学生"""
        if student_id in self.students:
            del self.students[student_id]
            print("学生删除成功！")
            return True
        else:
            print("未找到该学生！")
            return False
    
    def display_all_students(self):
        """显示所有学生信息"""
        if not self.students:
            print("系统中暂无学生信息！")
            return
        
        print("\n=== 所有学生信息 ===")
        for student in self.students.values():
            student.display_info()
        print("===================\n")


def main():
    """主函数，提供用户交互界面"""
    system = StudentManagementSystem()
    
    while True:
        print("\n=== 学生信息管理系统 ===")
        print("1. 添加学生")
        print("2. 查询学生")
        print("3. 更新学生信息")
        print("4. 删除学生")
        print("5. 显示所有学生")
        print("6. 退出系统")
        
        choice = input("请选择操作(1-6): ")
        
        if choice == '1':
            print("\n--- 添加学生 ---")
            student_id = input("请输入学号: ")
            name = input("请输入姓名: ")
            age = input("请输入年龄: ")
            grade = input("请输入成绩: ")
            system.add_student(student_id, name, age, grade)
        
        elif choice == '2':
            print("\n--- 查询学生 ---")
            student_id = input("请输入要查询的学号: ")
            system.search_student(student_id)
        
        elif choice == '3':
            print("\n--- 更新学生信息 ---")
            student_id = input("请输入要更新的学号: ")
            name = input("请输入新姓名(直接回车跳过): ")
            age = input("请输入新年龄(直接回车跳过): ")
            grade = input("请输入新成绩(直接回车跳过): ")
            
            # 处理空输入
            name = name if name else None
            age = int(age) if age else None
            grade = float(grade) if grade else None
            
            system.update_student(student_id, name, age, grade)
        
        elif choice == '4':
            print("\n--- 删除学生 ---")
            student_id = input("请输入要删除的学号: ")
            system.delete_student(student_id)
        
        elif choice == '5':
            system.display_all_students()
        
        elif choice == '6':
            print("感谢使用学生信息管理系统，再见！")
            break
        
        else:
            print("无效选择，请重新输入！")


if __name__ == "__main__":
    main()
