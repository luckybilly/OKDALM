package com.billy.demo.libs.moduleB;

import android.util.Log;

import com.billy.demo.libs.moduleA.ModuleA;

/**
 * module B
 * @author billy.qi
 * @since 16/7/11 17:02
 */
public class ModuleB {

    public ModuleB() {
        Log.i("ModuleB", "ModuleB created");
    }

    public void show() {
        Log.i("ModuleB", "showing...");
        new ModuleA().show();
    }

    @Override
    public String toString() {
        return "ModuleB";
    }
}
