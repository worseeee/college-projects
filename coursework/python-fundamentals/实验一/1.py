# 学生成绩管理系统
# 作者：刘胜炜 学号：0000000000

students = {}

def add_student():
    num = input("请输入学号：")
    name = input("请输入姓名：")
    score = float(input("请输入成绩："))
    students[num] = {"姓名": name, "成绩": score}
    print(f"学生 {name} 添加成功！")

def search_student():
    num = input("请输入要查询的学号：")
    if num in students:
        info = students[num]
        print(f"学号：{num}, 姓名：{info['姓名']}, 成绩：{info['成绩']}")
    else:
        print("未找到该学生！")

def show_all_students():
    if not students:
        print("暂无学生信息。")
    else:
        print("所有学生信息如下：")
        for num, info in students.items():
            print(f"学号：{num}, 姓名：{info['姓名']}, 成绩：{info['成绩']}")

def calculate_average():
    if not students:
        print("暂无学生信息，无法计算平均分。")
    else:
        total = sum(info["成绩"] for info in students.values())
        avg = total / len(students)
        print(f"学生平均成绩为：{avg:.2f}")

def main():
    while True:
        print("\n=== 学生成绩管理系统 ===")
        print("1. 添加学生")
        print("2. 查询学生")
        print("3. 显示所有学生")
        print("4. 计算平均分")
        print("5. 退出系统")
        choice = input("请选择功能（1-5）：")
        
        if choice == '1':
            add_student()
        elif choice == '2':
            search_student()
        elif choice == '3':
            show_all_students()
        elif choice == '4':
            calculate_average()
        elif choice == '5':
            print("感谢使用，再见！")
            break
        else:
            print("输入无效，请重新选择。")
if __name__ == "__main__":
    main()
