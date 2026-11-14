import java.util.*;

// 进程信息类
class Process {
    public String processName;  // 进程名字
    public int time;             // 进程需要时间
    public int level;            // 进程优先级
    public int leftTime;         // 进程剩余时间

    public Process(String name, int time, int level) {
        this.processName = name;
        this.time = time;
        this.level = level;
        this.leftTime = time; // 初始化剩余时间为总时间
    }
}

public class ProcessScheduler {
    private static Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        System.out.println("选择调度算法:");
        System.out.println("1:FIFO 2:时间片轮转 3:优先级调度 4:最短作业优先");
        int choice = scanner.nextInt();
        scanner.nextLine(); // 消耗换行符

        System.out.print("输入进程个数:");
        int num = scanner.nextInt();
        System.out.print("输入时间片大小:");
        int timePice = scanner.nextInt();
        scanner.nextLine();

        List<Process> processes = new ArrayList<>();
        for (int i = 0; i < num; i++) {
            System.out.printf("输入第%d个进程的名字、CPU时间和优先级:", i + 1);
            String name = scanner.next();
            int cpuTime = scanner.nextInt();
            int level = scanner.nextInt();
            processes.add(new Process(name, cpuTime, level));
        }

        // 初始化剩余时间
        for (Process p : processes) {
            p.leftTime = p.time;
        }

        // 输出表头
        System.out.println("进程名字\t占用CPU时间\t剩余时间\t优先级\t状态");

        switch (choice) {
            case 1:
                fifo(new ArrayList<>(processes), timePice);
                break;
            case 2:
                timeTurn(new ArrayList<>(processes), timePice);
                break;
            case 3:
                priority(new ArrayList<>(processes), timePice);
                break;
            case 4:
                sjf(new ArrayList<>(processes), timePice);
                break;
            default:
                System.out.println("无效选择");
        }
    }

    // 1. 先来先服务算法 (FIFO)
    private static void fifo(List<Process> queue, int timePice) {
        while (!queue.isEmpty()) {
            Process current = queue.get(0);
            if (current.leftTime <= 0) {
                System.out.println("进程" + current.processName + "已执行完毕!");
                queue.remove(0);
                continue;
            }
            // 执行时间片
            current.leftTime -= timePice;
            current.level -= 1;
            printStatus(current, "运行", queue.subList(1, queue.size()));
            waitForInput();
        }
        System.out.println("所有进程已执行完毕!");
    }

    // 2. 时间片轮转算法 (RR)
    private static void timeTurn(List<Process> queue, int timePice) {
        while (!queue.isEmpty()) {
            Process current = queue.get(0);
            if (current.leftTime <= 0) {
                System.out.println("进程" + current.processName + "已执行完毕!");
                queue.remove(0);
                continue;
            }
            // 执行时间片
            current.leftTime -= timePice;
            current.level -= 1;
            printStatus(current, "运行", queue.subList(1, queue.size()));

            // 移动到队尾（若未完成）
            if (current.leftTime > 0) {
                queue.remove(0);
                queue.add(current);
            } else {
                queue.remove(0);
            }
            waitForInput();
        }
        System.out.println("所有进程已执行完毕!");
    }

    // 3. 优先级调度算法 (PRIOR)
    private static void priority(List<Process> queue, int timePice) {
        while (!queue.isEmpty()) {
            // 按优先级降序排序（优先级数值越大越优先）
            queue.sort((p1, p2) -> Integer.compare(p2.level, p1.level));
            Process current = queue.get(0);

            if (current.leftTime <= 0) {
                System.out.println("进程" + current.processName + "已执行完毕!");
                queue.remove(0);
                continue;
            }
            // 执行时间片
            current.leftTime -= timePice;
            current.level -= 1;
            List<Process> waiting = queue.subList(1, queue.size());
            // 第一个等待进程为"就绪"，其余为"等待"
            printStatus(current, "运行", waiting, true);
            waitForInput();
        }
        System.out.println("所有进程已执行完毕!");
    }

    // 4. 最短作业优先算法 (SJF)
    private static void sjf(List<Process> queue, int timePice) {
        // 按所需时间升序排序
        queue.sort(Comparator.comparingInt(p -> p.time));

        while (!queue.isEmpty()) {
            Process current = queue.get(0);
            if (current.leftTime <= 0) {
                System.out.println("进程" + current.processName + "已执行完毕!");
                queue.remove(0);
                continue;
            }
            // 执行时间片
            current.leftTime -= timePice;
            current.level -= 1;
            printStatus(current, "运行", queue.subList(1, queue.size()));
            waitForInput();
        }
        System.out.println("所有进程已执行完毕!");
    }

    // 通用状态打印方法
    private static void printStatus(Process running, String status, List<Process> waiting) {
        printStatus(running, status, waiting, false);
    }

    private static void printStatus(Process running, String status, List<Process> waiting, boolean isPriority) {
        // 打印当前运行进程
        System.out.printf("%s\t\t%d\t\t%d\t\t%d\t\t%s\n",
                running.processName, running.time, running.leftTime, running.level, status);

        // 打印等待进程
        for (int i = 0; i < waiting.size(); i++) {
            Process p = waiting.get(i);
            String waitStatus = (isPriority && i == 0) ? "就绪" : "等待"; // 优先级调度第一个等待为就绪
            System.out.printf("%s\t\t%d\t\t%d\t\t%d\t\t%s\n",
                    p.processName, p.time, p.leftTime, p.level, waitStatus);
        }
        System.out.println();
    }

    // 等待用户输入继续
    private static void waitForInput() {
        System.out.print("请按任意键继续...");
        scanner.nextLine();
    }
}