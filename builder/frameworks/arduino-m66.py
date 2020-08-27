# WizIO 2020 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/platform-wizio-mtk

import os
from os.path import join
from shutil import copyfile
from SCons.Script import DefaultEnvironment, Builder
from colorama import Fore
from MT6261 import upload_app

def dev_uploader(target, source, env):
    return upload_app(env.boot, join(env.get("BUILD_DIR"), env.get("PROGNAME")), env.get("UPLOAD_PORT")) 

def dev_header(target, source, env):
    pass

def dev_create_template(env):
    pass 
                
def dev_compiler(env):
    env.Replace(
        BUILD_DIR = env.subst("$BUILD_DIR").replace("\\", "/"),
        AR="arm-none-eabi-ar",
        AS="arm-none-eabi-as",
        CC="arm-none-eabi-gcc",
        GDB="arm-none-eabi-gdb",
        CXX="arm-none-eabi-g++",
        OBJCOPY="arm-none-eabi-objcopy",
        RANLIB="arm-none-eabi-ranlib",
        SIZETOOL="arm-none-eabi-size",
        ARFLAGS=["rc"],
        SIZEPROGREGEXP=r"^(?:\.text|\.data|\.bootloader)\s+(\d+).*",
        SIZEDATAREGEXP=r"^(?:\.data|\.bss|\.noinit)\s+(\d+).*",
        SIZECHECKCMD="$SIZETOOL -A -d $SOURCES",
        SIZEPRINTCMD='$SIZETOOL --mcu=$BOARD_MCU -C -d $SOURCES',
        PROGSUFFIX=".elf", 
        PROGNAME = "ROM" 
    )
    env.cortex = [ "-marm", "-march=armv5te", "-mfloat-abi=soft", "-mfpu=vfp", "-mthumb-interwork" ]

def dev_init(env, platform):
    dev_create_template(env)
    dev_compiler(env)
    
    framework_dir = env.PioPlatform().get_package_dir("framework-wizio-mtk")
    env.core      = env.BoardConfig().get("build.core")  
    env.boot      = env.BoardConfig().get("build.boot", "0x20000") # the app address, default = 0x20000 
    sdk           = env.BoardConfig().get("build.sdk") 
    variant       = env.BoardConfig().get("build.variant")  
    heap          = env.BoardConfig().get("build.heap", "1048576") # default heap size 1M       

    fatfs = env.BoardConfig().get("build.use_fatfs", '0')
    FATFS_D = [ '', 'USE_FATFS' ][ fatfs != '0' ]
    FATFS_I = [ '', join(framework_dir, 'library', 'fatfs') ][ fatfs != '0' ]

    disable_nano = env.BoardConfig().get("build.disable_nano", "0x0") # defaut nano is enabled
    if disable_nano == "0":
        nano = ["-specs=nano.specs", "-u", "_printf_float", "-u", "_scanf_float" ]
    else: 
        nano = []

    script = join(framework_dir, platform, 'cores', env.core, "cpp_have_bootloader.ld") 

    env.Append(
        ASFLAGS=[ env.cortex, "-x", "assembler-with-cpp" ],        
        CPPDEFINES = [                         
            platform.upper()+"=200", 
            "BOOT_SIZE=" + env.boot,
            "HEAP_SIZE=" + heap,
            FATFS_D,
        ],        
        CPPPATH = [            
            join(framework_dir, platform, platform),
            join(framework_dir, platform, "cores", env.core),
            join(framework_dir, platform, "variants", variant),
            join(framework_dir, 'sdk', sdk, 'include'),  
            join("$PROJECT_DIR"),               
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include"),
            FATFS_I,         
        ],        
        CFLAGS = [
            env.cortex,
            "-Os",                                                       
            "-fdata-sections",      
            "-ffunction-sections",              
            "-fno-strict-aliasing",
            "-fno-zero-initialized-in-bss", 
            "-fsingle-precision-constant",                                                 
            "-Wall", 
            "-Wfatal-errors",
            "-Wno-strict-prototypes",
            "-Wno-unused-function",
            "-Wno-unused-but-set-variable",
            "-Wno-unused-variable",
            "-Wno-unused-value", 
            "-Wno-discarded-qualifiers",    
            "-mno-unaligned-access",                   
        ],     
        CXXFLAGS = [                               
            "-fno-rtti",
            "-fno-exceptions", 
            "-fno-non-call-exceptions",
            "-fno-use-cxa-atexit",
            "-fno-threadsafe-statics",
        ], 
        CCFLAGS = [
            env.cortex,
            "-Os",            
            "-fdata-sections",      
            "-ffunction-sections",              
            "-fno-strict-aliasing",
            "-fno-zero-initialized-in-bss",                                                  
            "-Wall", 
            "-Wfatal-errors",
            "-Wno-unused-function",
            "-Wno-unused-but-set-variable",
            "-Wno-unused-variable",
            "-Wno-unused-value",
            "-mno-unaligned-access",                                                       
        ],                      
        LINKFLAGS = [ 
            env.cortex,
            "-Os",    
            "-nostartfiles",   
            "-mno-unaligned-access",
            "-Wall", 
            "-Wfatal-errors",            
            "-fno-use-cxa-atexit",     
            "-fno-zero-initialized-in-bss",                                           
            "-Xlinker", "--gc-sections",                           
            "-Wl,--gc-sections", 
            "--entry=__isr_vectors",
            "-Xlinker", "--defsym=_BOOT_=" + env.boot, 
            nano                      
        ],
        LIBSOURCE_DIRS=[ join(framework_dir, platform, "libraries") ],  #arduino libraries 
        LDSCRIPT_PATH = script, 
        LIBS = [ "gcc", "m" ],               
        BUILDERS = dict(
            ElfToBin = Builder(
                action = env.VerboseAction(" ".join([
                    "$OBJCOPY",
                    "-O",
                    "binary",
                    "$SOURCES",
                    "$TARGET",
                ]), "Building $TARGET"),
                suffix = ""
            ),    
            MakeHeader = Builder( 
                action = env.VerboseAction(dev_header, "Building done"),
                suffix = ".ini"
            )       
        ), 
        UPLOADCMD = dev_uploader
    )
    
    libs = []   
     
    #ARDUINO  
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_" + platform),
            join(framework_dir, platform, platform),
    ))     
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_core"),
            join(framework_dir, platform, "cores", env.core),
    ))    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_variant"),
            join(framework_dir, platform, "variants", variant),
    ))  

    # SDK   
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", '_' + sdk + "_hal"),
            join(framework_dir, 'sdk', sdk, "hal"),
    ))      
   
    # PROJECT    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom"), 
            join("$PROJECT_DIR", "lib"),                       
    ))         

    if fatfs != '0':
        libs.append(
            env.BuildLibrary(
                join("$BUILD_DIR", '_' + sdk + "_fatfs"),
                join(framework_dir, 'library', "fatfs"),
        ))            

    env.Append(LIBS = libs)   
