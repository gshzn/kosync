export namespace main {
	
	export class KoboDevice {
	    name: string;
	    mountPath: string;
	
	    static createFrom(source: any = {}) {
	        return new KoboDevice(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.mountPath = source["mountPath"];
	    }
	}

}

