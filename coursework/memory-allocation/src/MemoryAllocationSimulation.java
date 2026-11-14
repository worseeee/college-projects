import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

public class MemoryAllocationSimulation {

    static class MemoryBlock {
        int startAddress;
        int size;
        boolean allocated;

        MemoryBlock(int startAddress, int size) {
            this.startAddress = startAddress;
            this.size = size;
            this.allocated = false;
        }

        @Override
        public String toString() {
            return String.format("%-8d %-8d", startAddress, size);
        }
    }

    static class Process {
        String name;
        int startAddress;
        int size;

        Process(String name, int startAddress, int size) {
            this.name = name;
            this.startAddress = startAddress;
            this.size = size;
        }
    }

    private static final int TOTAL_MEMORY = 640;
    private static final int OS_RESERVED = 40;
    private static final int MIN_FRAGMENT_SIZE = 10;

    private final List<MemoryBlock> freeList = new ArrayList<>();
    private final List<Process> allocatedList = new ArrayList<>();

    public MemoryAllocationSimulation() {
        // 初始化内存：操作系统占用40K，剩余600K空闲
        freeList.add(new MemoryBlock(OS_RESERVED, TOTAL_MEMORY - OS_RESERVED));
    }

    // 内存分配（最适合适应算法）
    public boolean allocateMemory(String name, int size) {
        // 按大小排序空闲分区（最适合适应算法）
        freeList.sort(Comparator.comparingInt(b -> b.size));

        for (MemoryBlock block : freeList) {
            if (!block.allocated && block.size >= size) {
                // 找到足够大的空闲块
                if (block.size - size >= MIN_FRAGMENT_SIZE) {
                    // 拆分空闲块
                    MemoryBlock newBlock = new MemoryBlock(
                            block.startAddress + size,
                            block.size - size
                    );
                    freeList.add(newBlock);

                    block.size = size;
                    allocatedList.add(new Process(name, block.startAddress, size));
                    block.allocated = true;
                } else {
                    // 整个块分配
                    allocatedList.add(new Process(name, block.startAddress, block.size));
                    block.allocated = true;
                }

                // 移除已分配块
                freeList.removeIf(b -> b.allocated);
                return true;
            }
        }
        return false;
    }

    // 内存释放
    public void releaseMemory(String name) {
        Process processToRemove = null;
        for (Process p : allocatedList) {
            if (p.name.equals(name)) {
                // 添加到空闲列表
                freeList.add(new MemoryBlock(p.startAddress, p.size));
                processToRemove = p;
                break;
            }
        }
        if (processToRemove != null) {
            allocatedList.remove(processToRemove);
        }
    }

    // 打印当前内存状态
    public void printMemoryStatus(String time) {
        System.out.println("\n" + time + "时刻内存状态:");
        System.out.println("已分配进程:");
        System.out.println("进程名  起始地址  大小");
        for (Process p : allocatedList) {
            System.out.printf("%-8s %-8d %-8d\n", p.name, p.startAddress, p.size);
        }

        System.out.println("\n空闲分区:");
        System.out.println("起始地址  大小");
        for (MemoryBlock block : freeList) {
            System.out.println(block);
        }
        System.out.println("--------------------------------");
    }

    public static void main(String[] args) {
        MemoryAllocationSimulation simulator = new MemoryAllocationSimulation();

        // t1时刻：分配A(80K), B(60K), C(100K)
        simulator.allocateMemory("A", 80);
        simulator.allocateMemory("B", 60);
        simulator.allocateMemory("C", 100);
        simulator.printMemoryStatus("t1");

        // t2时刻：释放B
        simulator.releaseMemory("B");
        simulator.printMemoryStatus("t2");

        // t3时刻：分配D(50K)
        simulator.allocateMemory("D", 50);
        simulator.printMemoryStatus("t3");

        // t4时刻：释放C和A
        simulator.releaseMemory("C");
        simulator.releaseMemory("A");
        simulator.printMemoryStatus("t4");

        // t5时刻：释放D
        simulator.releaseMemory("D");
        simulator.printMemoryStatus("t5");
    }
}