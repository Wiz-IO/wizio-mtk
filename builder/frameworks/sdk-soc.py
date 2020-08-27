# WizIO 2020 Georgi Angelov
#   http://www.wizio.eu/
#   https://github.com/Wiz-IO/platform-mt6261

import os
from os.path import join
from shutil import copyfile
from SCons.Script import DefaultEnvironment, Builder
from colorama import Fore
from MT6261 import upload_app

def dev_uploader(target, source, env):
    return upload_app("m66", join(env.get("BUILD_DIR"), env.get("PROGNAME")), env.get("UPLOAD_PORT")) 

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
    env.core    = env.BoardConfig().get("build.core")   
    env.heap    = env.BoardConfig().get("build.heap", "1048576")        # default heap size        

    disable_nano = env.BoardConfig().get("build.disable_nano", "0")    # defaut nano is enabled
    if disable_nano == "0":
        nano = ["-specs=nano.specs", "-u", "_printf_float", "-u", "_scanf_float" ]
    else: 
        nano = []

    print( "MT6261 SDK", env.core.upper())
    print("--->", join(framework_dir, platform) )
    env.Append(
        ASFLAGS=[ env.cortex, "-x", "assembler-with-cpp" ],        
        CPPDEFINES = [                         
            platform.upper(),                            
        ],        
        CPPPATH = [            
            join(framework_dir, platform),
            join(framework_dir, platform, "include"),     
            join(framework_dir, platform, "sys"), 
            join(framework_dir, platform, "lib"), 
            join(framework_dir, platform, "lib", "MT6261"), 
            join(framework_dir, platform, "lib", "MT6261", "drivers"), 
            join(framework_dir, platform, "gui"), 
            join(framework_dir, platform, "freertos", "include"),
            join(framework_dir, platform, "freertos", "portable"),
            join("$PROJECT_DIR", "lib"),
            join("$PROJECT_DIR", "include")         
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
            "-Wstrict-prototypes",
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
            nano                      
        ],
        LIBSOURCE_DIRS=[
            join(framework_dir, platform, "sdk"),
        ],
        LDSCRIPT_PATH = join(framework_dir, "sdk", "sdk.ld"), 
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
     
    # SDK   
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", '_' + platform, "asm"),
            join(framework_dir, platform, "asm"),
    )) 
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", '_' + platform, "sys"),
            join(framework_dir, platform, "sys"),
    ))    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", '_' + platform, "lib"),
            join(framework_dir, platform, "lib"),
    ))      
   
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", '_' + platform, "freertos"),
            join(framework_dir, platform, "freertos"),
    )) 

    # PROJECT    
    libs.append(
        env.BuildLibrary(
            join("$BUILD_DIR", "_custom"), 
            join("$PROJECT_DIR", "lib"),                       
    ))         

    env.Append(LIBS = libs)   
