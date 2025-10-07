export interface Food {
	id: number;
	name: string;
	type: string;
	image: string;
	nutrition: {
		calories: number;
		protein: number;
		carbs: number;
		fat: number;
		fiber: number;
	};
	vitamins: string[];
	minerals: string[];
	benefits: string[];
	nutriScore: 'A' | 'B' | 'C' | 'D' | 'E';
}
