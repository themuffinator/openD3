#!/usr/bin/env python3
"""Exercise production GUI batch boundaries and the screen stretch of GUI layouts."""
from pathlib import Path
import shutil
import subprocess
import tempfile

from filesystem_case_segments import function_body

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = r'''
#include <cassert>
#include <cstdlib>
#include <cstring>
#include <vector>
enum { SS_GUI=1, SS_POST_PROCESS=2, MF_NEED_CURRENT_RENDER=1 };
struct idMaterial {
    int sort=SS_GUI, flags=0;
    int GetSort() const { return sort; }
    bool TestMaterialFlag(int f) const { return (flags&f)!=0; }
};
struct guiModelSurface_t { int numIndexes; const idMaterial* material; };
template<class T> struct List:std::vector<T> { using std::vector<T>::operator=; int Num() const { return int(this->size()); } };
struct idGuiModel { List<guiModelSurface_t> surfaces; bool HasSceneFeedback() const; };
struct renderCrop_t { int x=0,y=0,width=1280,height=720; };
struct { int uiViewportX=0,uiViewportY=0,uiViewportWidth=1280,uiViewportHeight=720,vidHeight=720; } glConfig;
struct View { bool isEditor=false; };
struct idRenderSystemLocal {
    bool useUIViewportFor2D=false; int currentRenderCrop=0,flushes=0;
    renderCrop_t renderCrops[2]; void* activeRenderTexture=nullptr; View* viewDef=nullptr;
    idGuiModel model; idGuiModel* guiModel=&model;
    void FlushGui() { ++flushes; model.surfaces.clear(); }
    void SetUseUIViewportFor2D(bool enable);
};
struct idStr { static int Icmp(const char*a,const char*b) {
    while (*a && *b) { int x=(*a>='A'&&*a<='Z')?*a+32:*a; int y=(*b>='A'&&*b<='Z')?*b+32:*b;
        if(x!=y)return x-y; ++a;++b; } return *a-*b;
} };
struct idRectangle { float x,y,w,h; };
struct idMath { static int ClampInt(int lo,int hi,int v) { return v<lo?lo:(v>hi?hi:v); } };
struct idWindow { enum { SCREEN_STRETCH_NONE=0, SCREEN_STRETCH_FILL, SCREEN_STRETCH_LEADING, SCREEN_STRETCH_TRAILING }; };
'''
CHECKS = r'''
int main() {
#if defined(OPEND3_RENDERER_VK_MODULE)
    constexpr int captureFlush = 0;
#else
    constexpr int captureFlush = 1;
#endif
    idRenderSystemLocal r;
    idMaterial ui, composite{SS_POST_PROCESS,0}, feedback{SS_GUI,MF_NEED_CURRENT_RENDER};
    // Ordinary retained/legacy quads with an identical viewport still batch.
    r.model.surfaces={{6,&ui}}; r.SetUseUIViewportFor2D(true);
    assert(r.flushes==0 && r.model.surfaces.size()==1);
    // GL's eager capture needs a boundary even if ordinary UI is last in the
    // batch. Vulkan's just-in-time capture keeps its existing batch intact.
    r.model.surfaces={{6,&composite},{6,&ui}}; r.SetUseUIViewportFor2D(false);
    assert(r.flushes==captureFlush && (r.model.surfaces.empty() == bool(captureFlush)));
    r.model.surfaces={{6,&feedback}}; r.SetUseUIViewportFor2D(true);
    assert(r.flushes==2*captureFlush);
    // Empty material changes must not turn harmless UI into an extra flush.
    r.model.surfaces={{0,&composite},{6,&ui},{0,nullptr}}; r.SetUseUIViewportFor2D(false);
    assert(r.flushes==2*captureFlush);
    glConfig.uiViewportX=100; glConfig.uiViewportWidth=1080;
    r.SetUseUIViewportFor2D(true); assert(r.flushes==2*captureFlush+1);
    r.SetUseUIViewportFor2D(true); assert(r.flushes==2*captureFlush+1);
    // screenstretchx/y (GUI layout patches): fill moves both edges out, left
    // and right one each; children are told how far the origin moved.
    float x=0,w=640;
    assert(openD3_ApplyScreenStretchAxis(idWindow::SCREEN_STRETCH_FILL,106,106,x,w)==-106 && x==-106 && w==852);
    x=0; w=365;
    assert(openD3_ApplyScreenStretchAxis(idWindow::SCREEN_STRETCH_LEADING,106,106,x,w)==-106 && x==-106 && w==471);
    x=397; w=243;
    assert(openD3_ApplyScreenStretchAxis(idWindow::SCREEN_STRETCH_TRAILING,106,106,x,w)==0 && x==397 && w==349);
    // A negative extent mirrors the material; the rectangle still runs x..x+|w|.
    x=384; w=-256;
    assert(openD3_ApplyScreenStretchAxis(idWindow::SCREEN_STRETCH_TRAILING,106,106,x,w)==0 && x==384 && w==-362);
    // A collapsed window (a closed dialog) stays collapsed; none leaves it.
    x=0; w=0;
    assert(openD3_ApplyScreenStretchAxis(idWindow::SCREEN_STRETCH_FILL,106,106,x,w)==0 && x==0 && w==0);
    x=10; w=20;
    assert(openD3_ApplyScreenStretchAxis(idWindow::SCREEN_STRETCH_NONE,106,106,x,w)==0 && x==10 && w==20);
    unsigned char stretch=0;
    assert(openD3_ParseScreenStretchToken("right",false,stretch) && stretch==idWindow::SCREEN_STRETCH_TRAILING);
    assert(openD3_ParseScreenStretchToken("top",true,stretch) && stretch==idWindow::SCREEN_STRETCH_LEADING);
    assert(!openD3_ParseScreenStretchToken("top",false,stretch));
    assert(openD3_ParseScreenStretchToken("9",false,stretch) && stretch==idWindow::SCREEN_STRETCH_TRAILING);
}
'''

MASK_SUPPORT = r'''
#include <algorithm>
#include <cassert>
#include <cctype>
#include <string>
struct idStr {
    std::string value;
    idStr(const char* s=""):value(s){}
    operator const char*() const { return value.c_str(); }
    int Length() const { return int(value.size()); }
    void BackSlashesToSlashes() { std::replace(value.begin(),value.end(),'\\','/'); }
    void ExtractFileExtension(idStr& out) const {
        auto dot=value.find_last_of('.'); out.value=dot==std::string::npos?"":value.substr(dot+1);
    }
    void StripFileExtension() { auto dot=value.find_last_of('.'); if(dot!=std::string::npos)value.resize(dot); }
    void DefaultFileExtension(const char* ext) { if(value.find_last_of('.')==std::string::npos)value+=ext; }
    int Icmp(const char* other) const {
        auto a=value,b=std::string(other);
        for(auto& c:a)c=std::tolower(c); for(auto& c:b)c=std::tolower(c); return a.compare(b);
    }
    static int Icmpn(const char* a,const char* b,int n) {
        return idStr(std::string(a).substr(0,n).c_str()).Icmp(std::string(b).substr(0,n).c_str());
    }
};
struct Files {
    bool present=true; int probes=0;
    int ReadFile(const char* name,void*) { ++probes; assert(std::string(name).find(".tga")!=std::string::npos); return present?128:-1; }
} files;
auto* fileSystem=&files;
'''
MASK_CHECKS = r'''
int main() {
    const std::string base="gfx/guis/hud/reticles/mgun_scope_distort";
    for(const char* suffix:{"","_left","_right","_top","_bottom"}) {
        auto name=base+suffix;
        assert(R_HasUncompressedLegacyScopeMask(name.c_str()));
        assert(R_HasUncompressedLegacyScopeMask((name+".tga").c_str()));
        files.present=false;
        assert(!R_HasUncompressedLegacyScopeMask(name.c_str())); // DDS-only packs retain fallback
        files.present=true;
    }
    assert(R_IsLegacyScopeDistortionMask("GFX\\GUIS\\HUD\\RETICLES\\MGUN_SCOPE_DISTORT.TGA"));
    const int probes=files.probes;
    for(const char* name:{static_cast<const char*>(nullptr),"gfx/guis/hud/reticles/mgun_scope_distort.dds",
            "gfx/guis/hud/reticles/mgun_scope_distort_mod.tga",
            "gfx/guis/hud/reticles/mgun_scope_grey.tga","textures/stone.tga"}) {
        assert(!R_HasUncompressedLegacyScopeMask(name));
    }
    assert(files.probes==probes);
}
'''


def main():
    (ROOT / '.tmp').mkdir(exist_ok=True)
    compiler = next((shutil.which(n) for n in ('clang++', 'g++', 'c++') if shutil.which(n)), None)
    assert compiler, 'C++ compiler required'
    bodies = '\n'.join(function_body((ROOT / path).read_text(), signature) for path, signature in [
        ('src/renderer/GuiModel.cpp', 'bool idGuiModel::HasSceneFeedback() const'),
        ('src/renderer/RenderSystem.cpp', 'void idRenderSystemLocal::SetUseUIViewportFor2D( bool enable )'),
    ])
    for path in ('src/ui/Window.cpp', 'src/ui/SimpleWindow.cpp'):
        assert 'openD3_ApplyScreenStretchAxis(' in (ROOT / path).read_text(), path
    with tempfile.TemporaryDirectory(prefix='legacy-feedback-', dir=ROOT / '.tmp') as temp:
        source = Path(temp) / 'check.cpp'
        binary = Path(temp) / 'check.exe'
        source.write_text(SUPPORT + bodies + '\n#include "' +
                          (ROOT / 'src/ui/LegacyGuiLayout.h').as_posix() + '"\n' + CHECKS)
        subprocess.run([compiler, '-std=c++17', str(source), '-o', str(binary)], cwd=ROOT, check=True)
        subprocess.run([str(binary)], cwd=ROOT, check=True)
        subprocess.run([compiler, '-std=c++17', '-DOPEND3_RENDERER_VK_MODULE', str(source), '-o', str(binary)], cwd=ROOT, check=True)
        subprocess.run([str(binary)], cwd=ROOT, check=True)
        mask = '#include "' + (ROOT / 'src/imagetools/LegacyScopeMask.h').as_posix() + '"\n'
        mask += function_body((ROOT / 'src/imagetools/Image_files.cpp').read_text(),
                              'static bool R_HasUncompressedLegacyScopeMask( const char *name )')
        source.write_text(MASK_SUPPORT + mask + MASK_CHECKS)
        subprocess.run([compiler, '-std=c++17', str(source), '-o', str(binary)], cwd=ROOT, check=True)
        subprocess.run([str(binary)], cwd=ROOT, check=True)
    print('legacy UI: feedback ordering, retained batching, GUI layout screen stretch and mask source policy passed')


if __name__ == '__main__':
    main()
