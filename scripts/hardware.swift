import Foundation
import Metal
print("Memory GiB:", ProcessInfo.processInfo.physicalMemory / 1073741824)
for d in MTLCopyAllDevices() { print("GPU:", d.name, "working GiB:", d.recommendedMaxWorkingSetSize / 1073741824) }
