/**
 * Class to make Osalausestaja work by processing lines given in System.in
 * and writing results to System.out
 */
package ut.ee.estnltk;

import java.util.Scanner;

import ee.ut.soras.osalau.Osalausestaja;

public class OsalausestajaCmdWrap {
	
	public static void main(String[] args) throws Exception {
		Osalausestaja osalausestaja = new Osalausestaja();
		Scanner sc = new Scanner(System.in);
		while (sc.hasNextLine()) {
			String line = sc.nextLine();
			String result = osalausestaja.osalausestaPyVabamorfJSON(line);
			System.out.println(result.replace("\n", "").replace("\r", ""));
			System.out.flush();
		}
	}
}
